"""Expenses Routes - Placeholder"""
from app.routes import expenses_bp
from flask import jsonify

@expenses_bp.route('', methods=['GET'])
def list_expenses():
    """List all expenses"""
    return jsonify({'message': 'Expenses list endpoint - coming soon'}), 200
