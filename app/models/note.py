"""Note Models"""
from app import db
from datetime import datetime

class NoteCategory(db.Model):
    """Note category model"""
    __tablename__ = 'note_categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_name = db.Column(db.String(100))
    color_code = db.Column(db.String(7))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    """Note model"""
    __tablename__ = 'notes'
    
    note_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('note_categories.category_id'))
    tags = db.Column(db.Text)  # JSON
    is_pinned = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    attachments = db.relationship('NoteAttachment', backref='note', lazy='dynamic', cascade='all, delete-orphan')

class NoteAttachment(db.Model):
    """Note attachment model"""
    __tablename__ = 'note_attachments'
    
    attachment_id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'), nullable=False)
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.Text)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
