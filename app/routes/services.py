"""Services Routes - Placeholder"""
from app.routes import services_bp
from flask import jsonify

@services_bp.route('', methods=['GET'])
def list_services():
    """List all services"""
    return jsonify({'message': 'Services list endpoint - coming soon'}), 200
