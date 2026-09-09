"""Tasks Routes - Placeholder"""
from app.routes import tasks_bp
from flask import jsonify

@tasks_bp.route('', methods=['GET'])
def list_tasks():
    """List all tasks"""
    return jsonify({'message': 'Tasks list endpoint - coming soon'}), 200
