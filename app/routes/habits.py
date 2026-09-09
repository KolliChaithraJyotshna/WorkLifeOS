"""Habits Routes"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.habit import Habit, HabitLog
from app.services.habit_service import HabitService
from app.routes import habits_bp
from datetime import datetime

# ============================================
# HABIT CRUD
# ============================================

@habits_bp.route('', methods=['POST'])
@jwt_required()
def create_habit():
    """Create habit"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('habit_name'):
        return jsonify({'error': 'Habit name required'}), 400
    
    try:
        habit = HabitService.create_habit(user_id, data)
        return jsonify({
            'message': 'Habit created',
            'habit': habit_to_dict(habit)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@habits_bp.route('', methods=['GET'])
@jwt_required()
def list_habits():
    """List habits"""
    user_id = get_jwt_identity()
    active_only = request.args.get('active', default='true').lower() == 'true'
    
    try:
        habits = HabitService.get_user_habits(user_id, active_only)
        return jsonify({
            'total': len(habits),
            'habits': [habit_to_dict(h) for h in habits]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@habits_bp.route('/<int:habit_id>', methods=['GET'])
@jwt_required()
def get_habit(habit_id):
    """Get habit details"""
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    return jsonify(habit_to_dict(habit)), 200

@habits_bp.route('/<int:habit_id>', methods=['PUT'])
@jwt_required()
def update_habit(habit_id):
    """Update habit"""
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    
    try:
        habit = HabitService.update_habit(habit_id, request.get_json())
        return jsonify({
            'message': 'Habit updated',
            'habit': habit_to_dict(habit)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@habits_bp.route('/<int:habit_id>', methods=['DELETE'])
@jwt_required()
def delete_habit(habit_id):
    """Delete habit"""
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    
    HabitService.delete_habit(habit_id)
    return jsonify({'message': 'Habit deleted'}), 200

# ============================================
# HABIT LOGGING
# ============================================

@habits_bp.route('/<int:habit_id>/log', methods=['POST'])
@jwt_required()
def log_habit(habit_id):
    """Log habit completion"""
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        log = HabitService.log_habit(
            habit_id,
            data.get('value', 1),
            data.get('notes', '')
        )
        return jsonify({
            'message': 'Habit logged',
            'log': log_to_dict(log)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@habits_bp.route('/<int:habit_id>/logs', methods=['GET'])
@jwt_required()
def get_logs(habit_id):
    """Get habit logs"""
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    
    days = request.args.get('days', default=30, type=int)
    logs = HabitService.get_habit_logs(habit_id, days)
    
    return jsonify({
        'habit_id': habit_id,
        'days': days,
        'total_logs': len(logs),
        'logs': [log_to_dict(l) for l in logs]
    }), 200

# ============================================
# STATISTICS
# ============================================

@habits_bp.route('/<int:habit_id>/statistics', methods=['GET'])
@habits_bp.route('/<int:habit_id>/stats', methods=['GET'])
@jwt_required()
def get_habit_stats(habit_id):
    """Get habit statistics"""
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404
    
    stats = HabitService.get_habit_statistics(habit_id)
    return jsonify(stats), 200

@habits_bp.route('/statistics/summary', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user habit statistics"""
    user_id = get_jwt_identity()
    stats = HabitService.get_user_statistics(user_id)
    return jsonify(stats), 200

# ============================================
# HELPER FUNCTIONS
# ============================================

def habit_to_dict(habit: Habit) -> dict:
    return {
        'habit_id': habit.habit_id,
        'habit_name': habit.habit_name,
        'description': habit.description,
        'category': habit.category,
        'frequency': habit.frequency,
        'target_count': habit.target_count,
        'target_unit': habit.target_unit,
        'start_date': habit.start_date.isoformat(),
        'goal_date': habit.goal_date.isoformat() if habit.goal_date else None,
        'color_code': habit.color_code,
        'is_active': habit.is_active,
        'created_at': habit.created_at.isoformat()
    }

def log_to_dict(log: HabitLog) -> dict:
    return {
        'log_id': log.log_id,
        'habit_id': log.habit_id,
        'log_date': log.log_date.isoformat(),
        'value': log.value,
        'notes': log.notes,
        'logged_at': log.logged_at.isoformat()
    }
