"""API Routes"""
from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
calendar_bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')
notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')
expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')
habits_bp = Blueprint('habits', __name__, url_prefix='/api/habits')
services_bp = Blueprint('services', __name__, url_prefix='/api/services')

# Import route handlers
from app.routes import auth, tasks, calendar, notes, expenses, habits, services

__all__ = ['auth_bp', 'tasks_bp', 'calendar_bp', 'notes_bp', 'expenses_bp', 'habits_bp', 'services_bp']
