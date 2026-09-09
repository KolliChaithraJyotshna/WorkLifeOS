"""Calendar Models"""
from app import db
from datetime import datetime

class Calendar(db.Model):
    """Calendar model"""
    __tablename__ = 'calendars'
    
    calendar_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    calendar_name = db.Column(db.String(150))
    color_code = db.Column(db.String(7))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    events = db.relationship('Event', backref='calendar', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'calendar_id': self.calendar_id,
            'calendar_name': self.calendar_name,
            'color_code': self.color_code,
            'is_primary': self.is_primary
        }

class Event(db.Model):
    """Event model"""
    __tablename__ = 'events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.calendar_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    timezone = db.Column(db.String(50))
    event_type = db.Column(db.String(50))
    attendees = db.Column(db.Text)  # JSON
    reminder_minutes = db.Column(db.Integer, default=15)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MeetingConflict(db.Model):
    """Meeting conflict model"""
    __tablename__ = 'meeting_conflicts'
    
    conflict_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    event_id_1 = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    event_id_2 = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    conflict_type = db.Column(db.String(50))
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    resolution_note = db.Column(db.Text)
