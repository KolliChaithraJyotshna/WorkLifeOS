"""Expense Service - Business Logic"""
from app import db
from app.models.expense import Expense, ExpenseCategory, Invoice, InvoiceItem
from datetime import datetime, date
from sqlalchemy import and_, func
from decimal import Decimal

class ExpenseService:
    """Service for expense operations"""
    
    @staticmethod
    def create_category(user_id: int, category_name: str, description: str = '') -> ExpenseCategory:
        """Create expense category"""
        category = ExpenseCategory(
            user_id=user_id,
            category_name=category_name,
            description=description
        )
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def get_user_categories(user_id: int) -> list:
        """Get all expense categories for user"""
        return ExpenseCategory.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def create_expense(user_id: int, data: dict) -> Expense:
        """Create a new expense"""
        expense = Expense(
            user_id=user_id,
            title=data.get('title'),
            description=data.get('description'),
            amount=Decimal(str(data.get('amount', 0))),
            currency=data.get('currency', 'USD'),
            category_id=data.get('category_id'),
            expense_date=datetime.strptime(data.get('expense_date'), '%Y-%m-%d').date() if data.get('expense_date') else date.today(),
            payment_method=data.get('payment_method'),
            vendor_name=data.get('vendor_name'),
            status=data.get('status', 'pending'),
            receipt_path=data.get('receipt_path')
        )
        db.session.add(expense)
        db.session.commit()
        return expense
    
    @staticmethod
    def update_expense(expense_id: int, data: dict) -> Expense:
        """Update an expense"""
        expense = Expense.query.get(expense_id)
        if not expense:
            return None
        
        if 'title' in data:
            expense.title = data['title']
        if 'description' in data:
            expense.description = data['description']
        if 'amount' in data:
            expense.amount = Decimal(str(data['amount']))
        if 'category_id' in data:
            expense.category_id = data['category_id']
        if 'status' in data:
            expense.status = data['status']
        if 'payment_method' in data:
            expense.payment_method = data['payment_method']
        if 'vendor_name' in data:
            expense.vendor_name = data['vendor_name']
        
        expense.updated_at = datetime.utcnow()
        db.session.commit()
        return expense
    
    @staticmethod
    def get_user_expenses(user_id: int, status: str = None, category_id: int = None,
                         start_date: date = None, end_date: date = None) -> list:
        """Get expenses with filters"""
        query = Expense.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if start_date and end_date:
            query = query.filter(and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            ))
        
        return query.order_by(Expense.expense_date.desc()).all()
    
    @staticmethod
    def get_monthly_expenses(user_id: int, year: int, month: int) -> list:
        """Get expenses for a specific month"""
        return Expense.query.filter(
            and_(
                Expense.user_id == user_id,
                func.extract('year', Expense.expense_date) == year,
                func.extract('month', Expense.expense_date) == month
            )
        ).order_by(Expense.expense_date.desc()).all()
    
    @staticmethod
    def get_expense_summary(user_id: int, start_date: date = None, end_date: date = None) -> dict:
        """Get expense summary/statistics"""
        query = Expense.query.filter_by(user_id=user_id)
        
        if start_date and end_date:
            query = query.filter(and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            ))
        
        expenses = query.all()
        
        total_amount = sum([float(e.amount) for e in expenses])
        pending_amount = sum([float(e.amount) for e in expenses if e.status == 'pending'])
        approved_amount = sum([float(e.amount) for e in expenses if e.status == 'approved'])
        reimbursed_amount = sum([float(e.amount) for e in expenses if e.status == 'reimbursed'])
        
        # By category
        by_category = {}
        for expense in expenses:
            cat_name = expense.category_id or 'Uncategorized'
            if cat_name not in by_category:
                by_category[cat_name] = 0
            by_category[cat_name] += float(expense.amount)
        
        return {
            'total_expenses': len(expenses),
            'total_amount': total_amount,
            'pending_amount': pending_amount,
            'approved_amount': approved_amount,
            'reimbursed_amount': reimbursed_amount,
            'by_category': by_category
        }
    
    @staticmethod
    def approve_expense(expense_id: int) -> Expense:
        """Approve an expense"""
        expense = Expense.query.get(expense_id)
        if expense:
            expense.status = 'approved'
            expense.updated_at = datetime.utcnow()
            db.session.commit()
        return expense
    
    @staticmethod
    def reject_expense(expense_id: int) -> Expense:
        """Reject an expense"""
        expense = Expense.query.get(expense_id)
        if expense:
            expense.status = 'rejected'
            expense.updated_at = datetime.utcnow()
            db.session.commit()
        return expense
    
    @staticmethod
    def delete_expense(expense_id: int) -> bool:
        """Delete an expense"""
        expense = Expense.query.get(expense_id)
        if not expense:
            return False
        db.session.delete(expense)
        db.session.commit()
        return True
    
    # ============================================
    # INVOICE OPERATIONS
    # ============================================
    
    @staticmethod
    def create_invoice(user_id: int, data: dict) -> Invoice:
        """Create a new invoice"""
        invoice = Invoice(
            user_id=user_id,
            invoice_number=data.get('invoice_number'),
            client_name=data.get('client_name'),
            client_email=data.get('client_email'),
            invoice_date=datetime.strptime(data.get('invoice_date'), '%Y-%m-%d').date(),
            due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date(),
            total_amount=Decimal(str(data.get('total_amount', 0))),
            currency=data.get('currency', 'USD'),
            status=data.get('status', 'draft'),
            description=data.get('description'),
            notes=data.get('notes')
        )
        db.session.add(invoice)
        db.session.commit()
        
        # Add items
        items = data.get('items', [])
        for item in items:
            ExpenseService.add_invoice_item(
                invoice.invoice_id,
                item.get('description'),
                item.get('quantity'),
                item.get('rate'),
                item.get('amount')
            )
        
        return invoice
    
    @staticmethod
    def add_invoice_item(invoice_id: int, description: str, quantity: Decimal,
                        rate: Decimal, amount: Decimal) -> InvoiceItem:
        """Add item to invoice"""
        item = InvoiceItem(
            invoice_id=invoice_id,
            description=description,
            quantity=Decimal(str(quantity)),
            rate=Decimal(str(rate)),
            amount=Decimal(str(amount))
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    @staticmethod
    def get_user_invoices(user_id: int, status: str = None) -> list:
        """Get invoices for user"""
        query = Invoice.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Invoice.invoice_date.desc()).all()
    
    @staticmethod
    def update_invoice_status(invoice_id: int, status: str, paid_date: date = None) -> Invoice:
        """Update invoice status"""
        invoice = Invoice.query.get(invoice_id)
        if invoice:
            invoice.status = status
            if status == 'paid' and paid_date:
                invoice.paid_date = paid_date
            invoice.updated_at = datetime.utcnow()
            db.session.commit()
        return invoice
    
    @staticmethod
    def get_invoice_statistics(user_id: int) -> dict:
        """Get invoice statistics"""
        invoices = Invoice.query.filter_by(user_id=user_id).all()
        
        draft = [i for i in invoices if i.status == 'draft']
        sent = [i for i in invoices if i.status == 'sent']
        paid = [i for i in invoices if i.status == 'paid']
        overdue = [i for i in invoices if i.status == 'overdue']
        
        return {
            'total_invoices': len(invoices),
            'draft_count': len(draft),
            'sent_count': len(sent),
            'paid_count': len(paid),
            'overdue_count': len(overdue),
            'total_amount': float(sum([i.total_amount for i in invoices])),
            'paid_amount': float(sum([i.total_amount for i in paid])),
            'pending_amount': float(sum([i.total_amount for i in draft + sent + overdue]))
        }
