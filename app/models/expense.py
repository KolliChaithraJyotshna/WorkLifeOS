"""Expense Models"""
from app import db
from datetime import datetime

class ExpenseCategory(db.Model):
    """Expense category model"""
    __tablename__ = 'expense_categories'
    
    expense_category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    """Expense model"""
    __tablename__ = 'expenses'
    
    expense_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.expense_category_id'), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, index=True)
    payment_method = db.Column(db.String(50))
    vendor_name = db.Column(db.String(150))
    status = db.Column(db.String(50), default='pending')
    receipt_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Invoice(db.Model):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    invoice_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    client_name = db.Column(db.String(150), nullable=False)
    client_email = db.Column(db.String(150))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(50), default='draft')
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    pdf_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_date = db.Column(db.Date)
    
    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')

class InvoiceItem(db.Model):
    """Invoice item model"""
    __tablename__ = 'invoice_items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id'), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Numeric(8, 2))
    rate = db.Column(db.Numeric(10, 2))
    amount = db.Column(db.Numeric(10, 2))
