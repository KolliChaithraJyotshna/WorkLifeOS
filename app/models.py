"""
Database models for WorkLifeOS
Defines User, Calendar, Task, Note, Expense, Habit, and Service models
"""

from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import json


class User(db.Model):
    """User model for authentication and account management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    timezone = db.Column(db.String(50), default='UTC')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calendars = db.relationship('Calendar', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    habits = db.relationship('Habit', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Calendar(db.Model):
    """Calendar model for event scheduling"""
    
    __tablename__ = 'calendars'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3498db')
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='calendar', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Calendar {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Event(db.Model):
    """Event model for calendar entries"""
    
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    timezone = db.Column(db.String(50), default='UTC')
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.String(500))  # RFC 5545 RRULE format
    attendees = db.Column(db.JSON, default={})  # Stores attendee info
    reminders = db.Column(db.JSON, default=[])  # Reminder times in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'calendar_id': self.calendar_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'location': self.location,
            'timezone': self.timezone,
            'is_recurring': self.is_recurring,
            'recurrence_rule': self.recurrence_rule,
            'attendees': self.attendees,
            'reminders': self.reminders,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Task(db.Model):
    """Task model for task management with Eisenhower Matrix"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, done, blocked
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    urgency_score = db.Column(db.Integer, default=5)  # 1-10 scale
    importance_score = db.Column(db.Integer, default=5)  # 1-10 scale
    due_date = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    category = db.Column(db.String(50))
    tags = db.Column(db.JSON, default=[])
    dependencies = db.Column(db.JSON, default=[])  # List of task IDs this task depends on
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))  # For team tasks
    progress = db.Column(db.Integer, default=0)  # 0-100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'urgency_score': self.urgency_score,
            'importance_score': self.importance_score,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'category': self.category,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'assigned_to': self.assigned_to,
            'progress': self.progress,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Note(db.Model):
    """Note model for information hub"""
    
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    tags = db.Column(db.JSON, default=[])
    attachments = db.Column(db.JSON, default=[])  # File paths/URLs
    is_pinned = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags,
            'attachments': self.attachments,
            'is_pinned': self.is_pinned,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Expense(db.Model):
    """Expense model for expense tracking and invoicing"""
    
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    category = db.Column(db.String(50), nullable=False)  # groceries, utilities, entertainment, etc.
    description = db.Column(db.Text)
    receipt_path = db.Column(db.String(255))
    expense_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, credit, debit, etc.
    tags = db.Column(db.JSON, default=[])
    is_reimbursable = db.Column(db.Boolean, default=False)
    reimbursement_status = db.Column(db.String(20), default='pending')  # pending, approved, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.amount} {self.currency}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'category': self.category,
            'description': self.description,
            'receipt_path': self.receipt_path,
            'expense_date': self.expense_date.isoformat(),
            'payment_method': self.payment_method,
            'tags': self.tags,
            'is_reimbursable': self.is_reimbursable,
            'reimbursement_status': self.reimbursement_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Habit(db.Model):
    """Habit model for habit tracking and accountability"""
    
    __tablename__ = 'habits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # health, productivity, learning, etc.
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    target_value = db.Column(db.Float)  # For habits with measurable goals
    target_unit = db.Column(db.String(50))  # minutes, miles, pages, etc.
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    color = db.Column(db.String(7), default='#3498db')
    reminders = db.Column(db.JSON, default=[])  # Times of day to remind
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    logs = db.relationship('HabitLog', backref='habit', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Habit {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'frequency': self.frequency,
            'target_value': self.target_value,
            'target_unit': self.target_unit,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'color': self.color,
            'reminders': self.reminders,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class HabitLog(db.Model):
    """Habit log for tracking daily/weekly habit completion"""
    
    __tablename__ = 'habit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=True)
    value = db.Column(db.Float)  # For habits with measurable goals
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HabitLog {self.habit_id} {self.log_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'log_date': self.log_date.isoformat(),
            'completed': self.completed,
            'value': self.value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class Service(db.Model):
    """Service model for local services directory"""
    
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # plumbing, electrical, cleaning, etc.
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    availability = db.Column(db.JSON, default={})  # Hours of operation
    price_range = db.Column(db.String(50))  # $ to $$$$$
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('ServiceReview', backref='service', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Service {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'average_rating': self.average_rating,
            'rating_count': self.rating_count,
            'availability': self.availability,
            'price_range': self.price_range,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ServiceReview(db.Model):
    """Review model for service ratings and feedback"""
    
    __tablename__ = 'service_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    would_recommend = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user for context
    reviewer = db.relationship('User', backref='reviews')
    
    def __repr__(self):
        return f'<ServiceReview {self.service_id} {self.rating}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'title': self.title,
            'review_text': self.review_text,
            'would_recommend': self.would_recommend,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
