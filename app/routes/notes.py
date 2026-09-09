"""Notes Routes - Placeholder"""
from app.routes import notes_bp
from flask import jsonify

@notes_bp.route('', methods=['GET'])
def list_notes():
    """List all notes"""
    return jsonify({'message': 'Notes list endpoint - coming soon'}), 200
