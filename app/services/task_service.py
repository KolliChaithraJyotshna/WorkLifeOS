"""Task Service - Business Logic"""
from app import db
from app.models.task import Task, TaskDependency, TaskHistory
from datetime import datetime, date
from sqlalchemy import and_, or_

class TaskService:
    """Service for task operations"""
    
    @staticmethod
    def calculate_priority_score(urgency: int, importance: int) -> str:
        """
        Calculate priority using Eisenhower Matrix:
        - High Urgency + High Importance = CRITICAL
        - High Urgency + Low Importance = URGENT
        - Low Urgency + High Importance = IMPORTANT
        - Low Urgency + Low Importance = LOW
        """
        score = (urgency * 10) + importance
        
        if urgency >= 8 and importance >= 8:
            return 'critical'
        elif urgency >= 7:
            return 'high'
        elif importance >= 7:
            return 'high'
        elif urgency >= 5 or importance >= 5:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def create_task(user_id: int, data: dict) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            title=data.get('title'),
            description=data.get('description'),
            due_date=data.get('due_date'),
            due_time=data.get('due_time'),
            category=data.get('category'),
            estimated_hours=data.get('estimated_hours'),
            urgency_score=data.get('urgency_score', 0),
            importance_score=data.get('importance_score', 0),
            assigned_to=data.get('assigned_to')
        )
        
        # Calculate priority based on scores
        task.priority = TaskService.calculate_priority_score(
            task.urgency_score,
            task.importance_score
        )
        
        db.session.add(task)
        db.session.commit()
        return task
    
    @staticmethod
    def update_task(task: Task, data: dict, user_id: int) -> Task:
        """Update task and track changes"""
        changes = []
        old_status = task.status
        old_priority = task.priority
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
        if 'due_date' in data:
            task.due_date = data['due_date']
        if 'due_time' in data:
            task.due_time = data['due_time']
        if 'category' in data:
            task.category = data['category']
        if 'progress_percentage' in data:
            task.progress_percentage = data['progress_percentage']
        if 'urgency_score' in data:
            task.urgency_score = data['urgency_score']
        if 'importance_score' in data:
            task.importance_score = data['importance_score']
            # Recalculate priority
            task.priority = TaskService.calculate_priority_score(
                task.urgency_score,
                task.importance_score
            )
        if 'actual_hours' in data:
            task.actual_hours = data['actual_hours']
        
        task.updated_at = datetime.utcnow()
        
        # Log changes
        if old_status != task.status or old_priority != task.priority:
            history = TaskHistory(
                task_id=task.task_id,
                user_id=user_id,
                old_status=old_status,
                new_status=task.status,
                old_priority=old_priority,
                new_priority=task.priority,
                change_description=f"Status: {old_status} → {task.status}"
            )
            db.session.add(history)
        
        db.session.commit()
        return task
    
    @staticmethod
    def get_user_tasks(user_id: int, status: str = None, priority: str = None, 
                      due_date: date = None, assigned_only: bool = False) -> list:
        """Get filtered tasks for user"""
        query = Task.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        if due_date:
            query = query.filter_by(due_date=due_date)
        if assigned_only:
            query = query.filter(Task.assigned_to == user_id)
        
        return query.order_by(Task.urgency_score.desc(), Task.importance_score.desc()).all()
    
    @staticmethod
    def get_overdue_tasks(user_id: int) -> list:
        """Get overdue tasks"""
        today = date.today()
        return Task.query.filter(
            and_(
                Task.user_id == user_id,
                Task.due_date < today,
                Task.status != 'completed'
            )
        ).all()
    
    @staticmethod
    def get_upcoming_tasks(user_id: int, days: int = 7) -> list:
        """Get upcoming tasks for next N days"""
        today = date.today()
        from datetime import timedelta
        future_date = today + timedelta(days=days)
        
        return Task.query.filter(
            and_(
                Task.user_id == user_id,
                Task.due_date >= today,
                Task.due_date <= future_date,
                Task.status != 'completed'
            )
        ).order_by(Task.due_date).all()
    
    @staticmethod
    def add_dependency(blocking_task_id: int, blocked_task_id: int, 
                      dependency_type: str = 'must_complete') -> TaskDependency:
        """Add task dependency"""
        # Check if dependency already exists
        existing = TaskDependency.query.filter_by(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id
        ).first()
        
        if existing:
            return existing
        
        dependency = TaskDependency(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=dependency_type
        )
        db.session.add(dependency)
        db.session.commit()
        return dependency
    
    @staticmethod
    def get_blocking_tasks(task_id: int) -> list:
        """Get tasks that block this task"""
        dependencies = TaskDependency.query.filter_by(blocked_task_id=task_id).all()
        return [Task.query.get(dep.blocking_task_id) for dep in dependencies]
    
    @staticmethod
    def get_blocked_tasks(task_id: int) -> list:
        """Get tasks blocked by this task"""
        dependencies = TaskDependency.query.filter_by(blocking_task_id=task_id).all()
        return [Task.query.get(dep.blocked_task_id) for dep in dependencies]
    
    @staticmethod
    def can_complete_task(task_id: int) -> tuple:
        """
        Check if task can be completed
        Returns: (can_complete: bool, blocking_tasks: list)
        """
        blocking_tasks = TaskService.get_blocking_tasks(task_id)
        uncompleted_blockers = [
            t for t in blocking_tasks 
            if t.status != 'completed'
        ]
        
        return (len(uncompleted_blockers) == 0, uncompleted_blockers)
    
    @staticmethod
    def complete_task(task_id: int, user_id: int) -> Task:
        """Complete a task"""
        task = Task.query.get(task_id)
        if not task:
            return None
        
        can_complete, blockers = TaskService.can_complete_task(task_id)
        if not can_complete:
            raise ValueError(f"Cannot complete task. Blocked by {len(blockers)} task(s)")
        
        task.status = 'completed'
        task.progress_percentage = 100
        task.completed_at = datetime.utcnow()
        
        # Log completion
        history = TaskHistory(
            task_id=task_id,
            user_id=user_id,
            old_status='in_progress',
            new_status='completed',
            change_description='Task completed'
        )
        db.session.add(history)
        db.session.commit()
        return task
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        """Delete a task"""
        task = Task.query.get(task_id)
        if not task:
            return False
        
        db.session.delete(task)
        db.session.commit()
        return True
    
    @staticmethod
    def get_task_statistics(user_id: int) -> dict:
        """Get task statistics for user"""
        tasks = Task.query.filter_by(user_id=user_id).all()
        
        completed = len([t for t in tasks if t.status == 'completed'])
        in_progress = len([t for t in tasks if t.status == 'in_progress'])
        todo = len([t for t in tasks if t.status == 'todo'])
        overdue = len(TaskService.get_overdue_tasks(user_id))
        
        total_estimated = sum([t.estimated_hours or 0 for t in tasks if t.status != 'completed'])
        total_actual = sum([t.actual_hours or 0 for t in tasks if t.status == 'completed'])
        
        completion_rate = (completed / len(tasks) * 100) if tasks else 0
        
        return {
            'total_tasks': len(tasks),
            'completed': completed,
            'in_progress': in_progress,
            'todo': todo,
            'overdue': overdue,
            'completion_rate': round(completion_rate, 2),
            'total_estimated_hours': float(total_estimated),
            'total_actual_hours': float(total_actual)
        }
