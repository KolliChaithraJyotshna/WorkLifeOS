"""Task Models"""
from app import db
from datetime import datetime

class Task(db.Model):
    """Task model"""
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='todo', index=True)
    due_date = db.Column(db.Date, index=True)
    due_time = db.Column(db.Time)
    category = db.Column(db.String(100))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    estimated_hours = db.Column(db.Numeric(5, 2))
    actual_hours = db.Column(db.Numeric(5, 2))
    urgency_score = db.Column(db.Integer, default=0)
    importance_score = db.Column(db.Integer, default=0)
    progress_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class TaskDependency(db.Model):
    """Task dependency model"""
    __tablename__ = 'task_dependencies'
    
    dependency_id = db.Column(db.Integer, primary_key=True)
    blocking_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    blocked_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    dependency_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TaskHistory(db.Model):
    """Task history model"""
    __tablename__ = 'task_history'
    
    history_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    old_priority = db.Column(db.String(20))
    new_priority = db.Column(db.String(20))
    change_description = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
