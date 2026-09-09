"""Habits Routes - Placeholder"""
from app.routes import habits_bp
from flask import jsonify

@habits_bp.route('', methods=['GET'])
def list_habits():
    """List all habits"""
    return jsonify({'message': 'Habits list endpoint - coming soon'}), 200
