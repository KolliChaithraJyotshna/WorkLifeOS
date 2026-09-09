"""Habit Models"""
from app import db
from datetime import datetime

class Habit(db.Model):
    """Habit model"""
    __tablename__ = 'habits'
    
    habit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    habit_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    target_count = db.Column(db.Integer, default=1)
    target_unit = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    goal_date = db.Column(db.Date)
    color_code = db.Column(db.String(7))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HabitLog(db.Model):
    """Habit log model"""
    __tablename__ = 'habit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.habit_id'), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

class HabitStreak(db.Model):
    """Habit streak model"""
    __tablename__ = 'habit_streaks'
    
    streak_id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.habit_id'), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    streak_count = db.Column(db.Integer, default=0)
    is_current_streak = db.Column(db.Boolean, default=True)
    longest_streak = db.Column(db.Integer, default=0)
