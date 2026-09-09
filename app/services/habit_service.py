"""Habit Service - Business Logic"""
from app import db
from app.models.habit import Habit, HabitLog, HabitStreak
from datetime import datetime, date, timedelta
from sqlalchemy import and_

class HabitService:
    """Service for habit operations"""
    
    @staticmethod
    def create_habit(user_id: int, data: dict) -> Habit:
        """Create a new habit"""
        habit = Habit(
            user_id=user_id,
            habit_name=data.get('habit_name'),
            description=data.get('description'),
            category=data.get('category'),
            frequency=data.get('frequency', 'daily'),
            target_count=data.get('target_count', 1),
            target_unit=data.get('target_unit'),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else date.today(),
            goal_date=datetime.strptime(data.get('goal_date'), '%Y-%m-%d').date() if data.get('goal_date') else None,
            color_code=data.get('color_code', '#10b981'),
            is_active=data.get('is_active', True)
        )
        db.session.add(habit)
        db.session.commit()
        
        # Create initial streak
        HabitService.initialize_streak(habit.habit_id)
        
        return habit
    
    @staticmethod
    def initialize_streak(habit_id: int) -> HabitStreak:
        """Initialize streak for a habit"""
        streak = HabitStreak(
            habit_id=habit_id,
            start_date=date.today(),
            streak_count=0,
            is_current_streak=True,
            longest_streak=0
        )
        db.session.add(streak)
        db.session.commit()
        return streak
    
    @staticmethod
    def get_user_habits(user_id: int, active_only: bool = True) -> list:
        """Get habits for user"""
        query = Habit.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @staticmethod
    def log_habit(habit_id: int, value: int = 1, notes: str = '') -> HabitLog:
        """Log habit completion"""
        log = HabitLog(
            habit_id=habit_id,
            log_date=date.today(),
            value=value,
            notes=notes
        )
        db.session.add(log)
        db.session.commit()
        
        # Update streak
        HabitService.update_streak(habit_id)
        
        return log
    
    @staticmethod
    def update_streak(habit_id: int):
        """Update habit streak based on logs"""
        habit = Habit.query.get(habit_id)
        streak = HabitStreak.query.filter_by(habit_id=habit_id, is_current_streak=True).first()
        
        if not streak:
            HabitService.initialize_streak(habit_id)
            streak = HabitStreak.query.filter_by(habit_id=habit_id, is_current_streak=True).first()
        
        # Calculate current streak
        logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.log_date.desc()).all()
        
        if not logs:
            return
        
        current_streak = 0
        today = date.today()
        check_date = today
        
        for log in logs:
            if log.log_date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        streak.streak_count = current_streak
        if current_streak > streak.longest_streak:
            streak.longest_streak = current_streak
        
        db.session.commit()
    
    @staticmethod
    def get_habit_logs(habit_id: int, days: int = 30) -> list:
        """Get habit logs for past N days"""
        start_date = date.today() - timedelta(days=days)
        return HabitLog.query.filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= start_date
            )
        ).order_by(HabitLog.log_date.desc()).all()
    
    @staticmethod
    def get_habit_statistics(habit_id: int) -> dict:
        """Get statistics for a habit"""
        habit = Habit.query.get(habit_id)
        if not habit:
            return {}
        
        logs = HabitLog.query.filter_by(habit_id=habit_id).all()
        streak = HabitStreak.query.filter_by(habit_id=habit_id, is_current_streak=True).first()
        
        # Last 30 days
        last_30_logs = HabitService.get_habit_logs(habit_id, 30)
        completion_rate = (len(last_30_logs) / 30) * 100 if last_30_logs else 0
        
        days_since_start = (date.today() - habit.start_date).days
        
        return {
            'habit_name': habit.habit_name,
            'total_logs': len(logs),
            'current_streak': streak.streak_count if streak else 0,
            'longest_streak': streak.longest_streak if streak else 0,
            'completion_rate_30days': round(completion_rate, 2),
            'days_since_start': days_since_start
        }
    
    @staticmethod
    def update_habit(habit_id: int, data: dict) -> Habit:
        """Update a habit"""
        habit = Habit.query.get(habit_id)
        if not habit:
            return None
        
        if 'habit_name' in data:
            habit.habit_name = data['habit_name']
        if 'description' in data:
            habit.description = data['description']
        if 'category' in data:
            habit.category = data['category']
        if 'target_count' in data:
            habit.target_count = data['target_count']
        if 'is_active' in data:
            habit.is_active = data['is_active']
        
        habit.updated_at = datetime.utcnow()
        db.session.commit()
        return habit
    
    @staticmethod
    def delete_habit(habit_id: int) -> bool:
        """Delete a habit"""
        habit = Habit.query.get(habit_id)
        if not habit:
            return False
        db.session.delete(habit)
        db.session.commit()
        return True
    
    @staticmethod
    def get_user_statistics(user_id: int) -> dict:
        """Get overall habit statistics for user"""
        habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
        
        total_logs = 0
        total_streaks = 0
        active_habits = len(habits)
        
        for habit in habits:
            logs = HabitLog.query.filter_by(habit_id=habit.habit_id).all()
            total_logs += len(logs)
            
            streak = HabitStreak.query.filter_by(habit_id=habit.habit_id, is_current_streak=True).first()
            if streak and streak.streak_count > 0:
                total_streaks += 1
        
        return {
            'active_habits': active_habits,
            'total_logs': total_logs,
            'habits_with_active_streaks': total_streaks,
            'average_streak': (total_streaks / active_habits) if active_habits > 0 else 0
        }
