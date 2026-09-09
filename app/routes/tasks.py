"""Tasks Routes"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task import Task
from app.services.task_service import TaskService
from app.routes import tasks_bp
from datetime import datetime

# ============================================
# TASK CRUD OPERATIONS
# ============================================

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validation
    if not data or not data.get('title'):
        return jsonify({'error': 'Task title is required'}), 400
    
    try:
        task = TaskService.create_task(user_id, data)
        return jsonify({
            'message': 'Task created successfully',
            'task': task_to_dict(task)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def list_tasks():
    """List tasks with filters"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    status = request.args.get('status')
    priority = request.args.get('priority')
    due_date = request.args.get('due_date')
    view = request.args.get('view', 'all')  # all, overdue, upcoming
    
    try:
        if view == 'overdue':
            tasks = TaskService.get_overdue_tasks(user_id)
        elif view == 'upcoming':
            tasks = TaskService.get_upcoming_tasks(user_id)
        else:
            tasks = TaskService.get_user_tasks(
                user_id,
                status=status,
                priority=priority,
                due_date=due_date
            )
        
        return jsonify({
            'total': len(tasks),
            'tasks': [task_to_dict(t) for t in tasks]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get specific task"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task_to_dict(task)), 200

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    try:
        task = TaskService.update_task(task, data, user_id)
        return jsonify({
            'message': 'Task updated successfully',
            'task': task_to_dict(task)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        TaskService.delete_task(task_id)
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# TASK STATUS & COMPLETION
# ============================================

@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    """Mark task as completed"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        task = TaskService.complete_task(task_id, user_id)
        return jsonify({
            'message': 'Task completed successfully',
            'task': task_to_dict(task)
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@tasks_bp.route('/<int:task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    """Update task status"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    
    valid_statuses = ['todo', 'in_progress', 'completed', 'blocked', 'cancelled']
    if status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    try:
        task = TaskService.update_task(task, {'status': status}, user_id)
        return jsonify({
            'message': f'Task status updated to {status}',
            'task': task_to_dict(task)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# TASK DEPENDENCIES
# ============================================

@tasks_bp.route('/<int:task_id>/dependencies', methods=['GET'])
@jwt_required()
def get_task_dependencies(task_id):
    """Get task dependencies"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    blocking_tasks = TaskService.get_blocking_tasks(task_id)
    blocked_tasks = TaskService.get_blocked_tasks(task_id)
    
    return jsonify({
        'task_id': task_id,
        'blocking_tasks': [task_to_dict(t) for t in blocking_tasks],
        'blocked_tasks': [task_to_dict(t) for t in blocked_tasks]
    }), 200

@tasks_bp.route('/<int:blocking_task_id>/blocks/<int:blocked_task_id>', methods=['POST'])
@jwt_required()
def add_task_dependency(blocking_task_id, blocked_task_id):
    """Add dependency: blocking_task blocks blocked_task"""
    user_id = get_jwt_identity()
    
    # Verify both tasks belong to user
    blocking = Task.query.filter_by(task_id=blocking_task_id, user_id=user_id).first()
    blocked = Task.query.filter_by(task_id=blocked_task_id, user_id=user_id).first()
    
    if not blocking or not blocked:
        return jsonify({'error': 'One or both tasks not found'}), 404
    
    try:
        dep_type = request.get_json().get('dependency_type', 'must_complete') if request.get_json() else 'must_complete'
        dependency = TaskService.add_dependency(blocking_task_id, blocked_task_id, dep_type)
        return jsonify({
            'message': 'Dependency added successfully',
            'blocking_task_id': blocking_task_id,
            'blocked_task_id': blocked_task_id,
            'dependency_type': dep_type
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@tasks_bp.route('/<int:task_id>/check-completion', methods=['GET'])
@jwt_required()
def check_task_completion(task_id):
    """Check if task can be completed"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(task_id=task_id, user_id=user_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    can_complete, blockers = TaskService.can_complete_task(task_id)
    
    return jsonify({
        'task_id': task_id,
        'can_complete': can_complete,
        'blocking_tasks_count': len(blockers),
        'blocking_tasks': [task_to_dict(t) for t in blockers]
    }), 200

# ============================================
# TASK ANALYTICS & STATISTICS
# ============================================

@tasks_bp.route('/statistics/summary', methods=['GET'])
@jwt_required()
def get_task_statistics():
    """Get task statistics for user"""
    user_id = get_jwt_identity()
    
    stats = TaskService.get_task_statistics(user_id)
    return jsonify(stats), 200

@tasks_bp.route('/priority-matrix', methods=['GET'])
@jwt_required()
def get_priority_matrix():
    """Get tasks organized by Eisenhower Matrix"""
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    
    matrix = {
        'critical': [],      # High Urgent + High Important
        'important': [],      # Low Urgent + High Important
        'urgent': [],         # High Urgent + Low Important
        'low_priority': []    # Low Urgent + Low Important
    }
    
    for task in tasks:
        if task.priority == 'critical':
            matrix['critical'].append(task_to_dict(task))
        elif task.priority == 'high' and task.importance_score > task.urgency_score:
            matrix['important'].append(task_to_dict(task))
        elif task.priority == 'high':
            matrix['urgent'].append(task_to_dict(task))
        else:
            matrix['low_priority'].append(task_to_dict(task))
    
    return jsonify(matrix), 200

# ============================================
# HELPER FUNCTIONS
# ============================================

def task_to_dict(task: Task) -> dict:
    """Convert task to dictionary"""
    return {
        'task_id': task.task_id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'due_time': task.due_time.isoformat() if task.due_time else None,
        'category': task.category,
        'urgency_score': task.urgency_score,
        'importance_score': task.importance_score,
        'progress_percentage': task.progress_percentage,
        'estimated_hours': float(task.estimated_hours) if task.estimated_hours else None,
        'actual_hours': float(task.actual_hours) if task.actual_hours else None,
        'assigned_to': task.assigned_to,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat(),
        'completed_at': task.completed_at.isoformat() if task.completed_at else None
    }
