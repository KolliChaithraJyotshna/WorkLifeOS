"""Tests for Task Service"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.services.task_service import TaskService
from datetime import datetime, date, timedelta

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def user(app):
    """Create test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

class TestTaskService:
    """Test task service"""
    
    def test_create_task(self, app, user):
        """Test creating a task"""
        with app.app_context():
            data = {
                'title': 'Test Task',
                'description': 'This is a test task',
                'urgency_score': 8,
                'importance_score': 9
            }
            task = TaskService.create_task(user.user_id, data)
            
            assert task.title == 'Test Task'
            assert task.priority == 'critical'
            assert task.status == 'todo'
    
    def test_priority_calculation(self, app):
        """Test priority calculation"""
        with app.app_context():
            assert TaskService.calculate_priority_score(9, 9) == 'critical'
            assert TaskService.calculate_priority_score(8, 2) == 'high'
            assert TaskService.calculate_priority_score(3, 8) == 'high'
            assert TaskService.calculate_priority_score(5, 5) == 'medium'
            assert TaskService.calculate_priority_score(2, 2) == 'low'
    
    def test_update_task(self, app, user):
        """Test updating a task"""
        with app.app_context():
            task = Task(user_id=user.user_id, title='Original')
            db.session.add(task)
            db.session.commit()
            
            data = {'title': 'Updated', 'status': 'in_progress'}
            updated = TaskService.update_task(task, data, user.user_id)
            
            assert updated.title == 'Updated'
            assert updated.status == 'in_progress'
    
    def test_get_overdue_tasks(self, app, user):
        """Test getting overdue tasks"""
        with app.app_context():
            yesterday = date.today() - timedelta(days=1)
            task = Task(
                user_id=user.user_id,
                title='Overdue Task',
                due_date=yesterday,
                status='todo'
            )
            db.session.add(task)
            db.session.commit()
            
            overdue = TaskService.get_overdue_tasks(user.user_id)
            assert len(overdue) == 1
            assert overdue[0].task_id == task.task_id
    
    def test_task_dependencies(self, app, user):
        """Test task dependencies"""
        with app.app_context():
            task1 = Task(user_id=user.user_id, title='Task 1')
            task2 = Task(user_id=user.user_id, title='Task 2')
            db.session.add_all([task1, task2])
            db.session.commit()
            
            # Add dependency
            TaskService.add_dependency(task1.task_id, task2.task_id)
            
            # Check relationships
            blockers = TaskService.get_blocking_tasks(task2.task_id)
            assert len(blockers) == 1
            assert blockers[0].task_id == task1.task_id
    
    def test_cannot_complete_blocked_task(self, app, user):
        """Test that blocked tasks cannot be completed"""
        with app.app_context():
            task1 = Task(user_id=user.user_id, title='Task 1', status='todo')
            task2 = Task(user_id=user.user_id, title='Task 2', status='todo')
            db.session.add_all([task1, task2])
            db.session.commit()
            
            # task1 blocks task2
            TaskService.add_dependency(task1.task_id, task2.task_id)
            
            # Try to complete task2
            can_complete, blockers = TaskService.can_complete_task(task2.task_id)
            assert not can_complete
            assert len(blockers) == 1

class TestTaskAPI:
    """Test task API endpoints"""
    
    def test_register_and_login(self, client):
        """Test user registration and login"""
        # Register
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'full_name': 'Test User'
        })
        assert response.status_code == 201
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        return data['access_token']
    
    def test_create_task_endpoint(self, client):
        """Test creating task via API"""
        token = self.test_register_and_login(client)
        
        response = client.post(
            '/api/tasks',
            json={
                'title': 'API Test Task',
                'description': 'Created via API',
                'urgency_score': 7,
                'importance_score': 8
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['task']['title'] == 'API Test Task'
    
    def test_list_tasks_endpoint(self, client):
        """Test listing tasks via API"""
        token = self.test_register_and_login(client)
        
        # Create tasks
        client.post(
            '/api/tasks',
            json={'title': 'Task 1'},
            headers={'Authorization': f'Bearer {token}'}
        )
        client.post(
            '/api/tasks',
            json={'title': 'Task 2'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # List tasks
        response = client.get(
            '/api/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
    
    def test_update_task_endpoint(self, client):
        """Test updating task via API"""
        token = self.test_register_and_login(client)
        
        # Create task
        create_response = client.post(
            '/api/tasks',
            json={'title': 'Original Title'},
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_response.get_json()['task']['task_id']
        
        # Update task
        response = client.put(
            f'/api/tasks/{task_id}',
            json={'title': 'Updated Title', 'status': 'in_progress'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['task']['title'] == 'Updated Title'
        assert data['task']['status'] == 'in_progress'
