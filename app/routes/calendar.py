"""Calendar Routes - Placeholder"""
from app.routes import calendar_bp
from flask import jsonify

@calendar_bp.route('', methods=['GET'])
def list_events():
    """List all calendar events"""
    return jsonify({'message': 'Calendar list endpoint - coming soon'}), 200
