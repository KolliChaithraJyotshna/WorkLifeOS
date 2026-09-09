"""Expenses Routes"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.expense import Expense, ExpenseCategory
from app.services.expense_service import ExpenseService
from app.routes import expenses_bp
from datetime import datetime, date

# ============================================
# EXPENSE CATEGORIES
# ============================================

@expenses_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create expense category"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('category_name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    try:
        category = ExpenseService.create_category(
            user_id,
            data.get('category_name'),
            data.get('description', '')
        )
        return jsonify({
            'message': 'Category created',
            'category': category_to_dict(category)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@expenses_bp.route('/categories', methods=['GET'])
@jwt_required()
def list_categories():
    """List expense categories"""
    user_id = get_jwt_identity()
    categories = ExpenseService.get_user_categories(user_id)
    return jsonify({
        'total': len(categories),
        'categories': [category_to_dict(c) for c in categories]
    }), 200

# ============================================
# EXPENSE CRUD
# ============================================

@expenses_bp.route('', methods=['POST'])
@jwt_required()
def create_expense():
    """Create expense"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('amount'):
        return jsonify({'error': 'Title and amount required'}), 400
    
    try:
        expense = ExpenseService.create_expense(user_id, data)
        return jsonify({
            'message': 'Expense created',
            'expense': expense_to_dict(expense)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@expenses_bp.route('', methods=['GET'])
@jwt_required()
def list_expenses():
    """List expenses with filters"""
    user_id = get_jwt_identity()
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        expenses = ExpenseService.get_user_expenses(user_id, status, category_id, start, end)
        return jsonify({
            'total': len(expenses),
            'expenses': [expense_to_dict(e) for e in expenses]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@expenses_bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """Get expense details"""
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(expense_id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    return jsonify(expense_to_dict(expense)), 200

@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """Update expense"""
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(expense_id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    try:
        expense = ExpenseService.update_expense(expense_id, request.get_json())
        return jsonify({
            'message': 'Expense updated',
            'expense': expense_to_dict(expense)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """Delete expense"""
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(expense_id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    ExpenseService.delete_expense(expense_id)
    return jsonify({'message': 'Expense deleted'}), 200

# ============================================
# EXPENSE ACTIONS
# ============================================

@expenses_bp.route('/<int:expense_id>/approve', methods=['POST'])
@jwt_required()
def approve_expense(expense_id):
    """Approve expense"""
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(expense_id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    expense = ExpenseService.approve_expense(expense_id)
    return jsonify({
        'message': 'Expense approved',
        'expense': expense_to_dict(expense)
    }), 200

# ============================================
# STATISTICS
# ============================================

@expenses_bp.route('/statistics/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Get expense summary"""
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    
    summary = ExpenseService.get_expense_summary(user_id, start, end)
    return jsonify(summary), 200

# ============================================
# INVOICES
# ============================================

@expenses_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create invoice"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('invoice_number') or not data.get('client_name'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        invoice = ExpenseService.create_invoice(user_id, data)
        return jsonify({
            'message': 'Invoice created',
            'invoice': invoice_to_dict(invoice)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@expenses_bp.route('/invoices', methods=['GET'])
@jwt_required()
def list_invoices():
    """List invoices"""
    user_id = get_jwt_identity()
    status = request.args.get('status')
    invoices = ExpenseService.get_user_invoices(user_id, status)
    return jsonify({
        'total': len(invoices),
        'invoices': [invoice_to_dict(i) for i in invoices]
    }), 200

# ============================================
# HELPER FUNCTIONS
# ============================================

def category_to_dict(category: ExpenseCategory) -> dict:
    return {
        'category_id': category.expense_category_id,
        'category_name': category.category_name,
        'description': category.description,
        'created_at': category.created_at.isoformat()
    }

def expense_to_dict(expense: Expense) -> dict:
    return {
        'expense_id': expense.expense_id,
        'title': expense.title,
        'amount': float(expense.amount),
        'currency': expense.currency,
        'category_id': expense.category_id,
        'status': expense.status,
        'expense_date': expense.expense_date.isoformat(),
        'vendor_name': expense.vendor_name,
        'payment_method': expense.payment_method,
        'created_at': expense.created_at.isoformat()
    }

def invoice_to_dict(invoice) -> dict:
    return {
        'invoice_id': invoice.invoice_id,
        'invoice_number': invoice.invoice_number,
        'client_name': invoice.client_name,
        'client_email': invoice.client_email,
        'total_amount': float(invoice.total_amount),
        'status': invoice.status,
        'invoice_date': invoice.invoice_date.isoformat(),
        'due_date': invoice.due_date.isoformat(),
        'paid_date': invoice.paid_date.isoformat() if invoice.paid_date else None,
        'created_at': invoice.created_at.isoformat()
    }
