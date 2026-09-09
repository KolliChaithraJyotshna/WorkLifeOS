"""
Utility functions and decorators for WorkLifeOS
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import re
from datetime import datetime


def token_required(f):
    """
    Decorator to require JWT token for protected routes
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


def validate_timezone(timezone):
    """Validate timezone string"""
    import pytz
    try:
        pytz.timezone(timezone)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False


def paginate_query(query, page=1, per_page=20):
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        tuple: (items, total, pages)
    """
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return paginated.items, paginated.total, paginated.pages


def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(message="Error", status_code=400, errors=None):
    """Create a standardized error response"""
    response = {
        'success': False,
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code


def parse_request_data():
    """
    Parse request data from JSON body
    
    Returns:
        dict: Parsed JSON data or empty dict
    """
    if request.is_json:
        return request.get_json()
    return {}


def get_current_user_id():
    """Get the current authenticated user's ID"""
    return get_jwt_identity()


def calculate_eisenhower_matrix(urgency, importance):
    """
    Calculate Eisenhower Matrix quadrant
    
    Quadrants:
    1. Urgent & Important - Do First
    2. Not Urgent & Important - Schedule
    3. Urgent & Not Important - Delegate
    4. Not Urgent & Not Important - Eliminate
    """
    if urgency >= 7 and importance >= 7:
        return "Q1_DO_FIRST"
    elif urgency < 7 and importance >= 7:
        return "Q2_SCHEDULE"
    elif urgency >= 7 and importance < 7:
        return "Q3_DELEGATE"
    else:
        return "Q4_ELIMINATE"


def calculate_priority_score(urgency_score, importance_score):
    """
    Calculate overall priority score
    
    Uses weighted formula: (urgency * 0.6) + (importance * 0.4)
    """
    return (urgency_score * 0.6) + (importance_score * 0.4)


def calculate_streak(habit_logs):
    """
    Calculate current streak for a habit
    
    Args:
        habit_logs: List of HabitLog objects sorted by date
    
    Returns:
        int: Current streak count
    """
    if not habit_logs:
        return 0
    
    streak = 0
    today = datetime.utcnow().date()
    
    for log in reversed(habit_logs):
        log_date = log.log_date.date()
        expected_date = today if streak == 0 else today - timedelta(days=streak)
        
        if log_date == expected_date and log.completed:
            streak += 1
        else:
            break
    
    return streak


def format_datetime(dt, timezone='UTC'):
    """Format datetime to ISO format string"""
    if dt is None:
        return None
    return dt.isoformat()


def parse_datetime(dt_string):
    """Parse ISO format datetime string"""
    try:
        return datetime.fromisoformat(dt_string)
    except (ValueError, TypeError):
        return None


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)
