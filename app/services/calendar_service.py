"""Calendar Service - Business Logic"""
from app import db
from app.models.calendar import Calendar, Event, MeetingConflict
from datetime import datetime, timedelta
import pytz
from sqlalchemy import and_, or_

class CalendarService:
    """Service for calendar and event operations"""
    
    @staticmethod
    def create_calendar(user_id: int, calendar_name: str, color_code: str = '#3b82f6', 
                       is_primary: bool = False) -> Calendar:
        """Create a new calendar for user"""
        calendar = Calendar(
            user_id=user_id,
            calendar_name=calendar_name,
            color_code=color_code,
            is_primary=is_primary
        )
        db.session.add(calendar)
        db.session.commit()
        return calendar
    
    @staticmethod
    def get_user_calendars(user_id: int) -> list:
        """Get all calendars for user"""
        return Calendar.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def create_event(calendar_id: int, data: dict) -> Event:
        """Create a new event"""
        event = Event(
            calendar_id=calendar_id,
            title=data.get('title'),
            description=data.get('description'),
            start_time=datetime.fromisoformat(data.get('start_time')),
            end_time=datetime.fromisoformat(data.get('end_time')),
            location=data.get('location'),
            timezone=data.get('timezone', 'UTC'),
            event_type=data.get('event_type', 'meeting'),
            attendees=data.get('attendees'),  # JSON string
            reminder_minutes=data.get('reminder_minutes', 15),
            is_recurring=data.get('is_recurring', False),
            recurrence_pattern=data.get('recurrence_pattern')
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Check for conflicts
        CalendarService.check_conflicts(calendar_id, event)
        
        return event
    
    @staticmethod
    def check_conflicts(calendar_id: int, new_event: Event) -> list:
        """Check for meeting conflicts"""
        calendar = Calendar.query.get(calendar_id)
        if not calendar:
            return []
        
        conflicts = []
        user_events = Event.query.filter_by(calendar_id=calendar_id).all()
        
        for existing_event in user_events:
            if existing_event.event_id == new_event.event_id:
                continue
            
            # Check for overlap
            if CalendarService.events_overlap(existing_event, new_event):
                conflict = MeetingConflict(
                    user_id=calendar.user_id,
                    event_id_1=existing_event.event_id,
                    event_id_2=new_event.event_id,
                    conflict_type='overlap'
                )
                db.session.add(conflict)
                conflicts.append(conflict)
            
            # Check for back-to-back meetings (warning)
            elif CalendarService.events_back_to_back(existing_event, new_event):
                conflict = MeetingConflict(
                    user_id=calendar.user_id,
                    event_id_1=existing_event.event_id,
                    event_id_2=new_event.event_id,
                    conflict_type='back_to_back'
                )
                db.session.add(conflict)
                conflicts.append(conflict)
        
        db.session.commit()
        return conflicts
    
    @staticmethod
    def events_overlap(event1: Event, event2: Event) -> bool:
        """Check if two events overlap"""
        return (
            event1.start_time < event2.end_time and
            event1.end_time > event2.start_time
        )
    
    @staticmethod
    def events_back_to_back(event1: Event, event2: Event, gap_minutes: int = 15) -> bool:
        """Check if events are back-to-back with minimal gap"""
        gap = timedelta(minutes=gap_minutes)
        
        # Event1 ends, then Event2 starts
        if event1.end_time <= event2.start_time <= (event1.end_time + gap):
            return True
        
        # Event2 ends, then Event1 starts
        if event2.end_time <= event1.start_time <= (event2.end_time + gap):
            return True
        
        return False
    
    @staticmethod
    def get_events_by_date(calendar_id: int, event_date: str) -> list:
        """Get events for a specific date"""
        from datetime import date as date_obj
        date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
        
        events = Event.query.filter_by(calendar_id=calendar_id).all()
        return [
            e for e in events
            if e.start_time.date() == date_obj
        ]
    
    @staticmethod
    def get_events_by_range(calendar_id: int, start_date: str, end_date: str) -> list:
        """Get events within a date range"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        return Event.query.filter(
            and_(
                Event.calendar_id == calendar_id,
                Event.start_time >= start,
                Event.end_time <= end
            )
        ).order_by(Event.start_time).all()
    
    @staticmethod
    def get_today_events(calendar_id: int) -> list:
        """Get today's events"""
        today = datetime.now().date()
        events = Event.query.filter_by(calendar_id=calendar_id).all()
        return [
            e for e in events
            if e.start_time.date() == today
        ]
    
    @staticmethod
    def get_upcoming_events(calendar_id: int, days: int = 7) -> list:
        """Get upcoming events for next N days"""
        now = datetime.now()
        future = now + timedelta(days=days)
        
        return Event.query.filter(
            and_(
                Event.calendar_id == calendar_id,
                Event.start_time >= now,
                Event.start_time <= future
            )
        ).order_by(Event.start_time).all()
    
    @staticmethod
    def update_event(event_id: int, data: dict) -> Event:
        """Update an event"""
        event = Event.query.get(event_id)
        if not event:
            return None
        
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time'])
        if 'location' in data:
            event.location = data['location']
        if 'timezone' in data:
            event.timezone = data['timezone']
        if 'reminder_minutes' in data:
            event.reminder_minutes = data['reminder_minutes']
        if 'attendees' in data:
            event.attendees = data['attendees']
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Recheck conflicts
        CalendarService.check_conflicts(event.calendar_id, event)
        
        return event
    
    @staticmethod
    def delete_event(event_id: int) -> bool:
        """Delete an event"""
        event = Event.query.get(event_id)
        if not event:
            return False
        
        db.session.delete(event)
        db.session.commit()
        return True
    
    @staticmethod
    def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """Convert datetime between timezones"""
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # Assume dt is naive, localize to source timezone
        if dt.tzinfo is None:
            dt = from_timezone.localize(dt)
        
        return dt.astimezone(to_timezone)
    
    @staticmethod
    def get_conflicts_for_user(user_id: int, resolved: bool = False) -> list:
        """Get all conflicts for user"""
        return MeetingConflict.query.filter_by(
            user_id=user_id,
            is_resolved=resolved
        ).all()
    
    @staticmethod
    def resolve_conflict(conflict_id: int, resolution_note: str = '') -> bool:
        """Mark conflict as resolved"""
        conflict = MeetingConflict.query.get(conflict_id)
        if not conflict:
            return False
        
        conflict.is_resolved = True
        conflict.resolution_note = resolution_note
        db.session.commit()
        return True
    
    @staticmethod
    def get_calendar_statistics(calendar_id: int) -> dict:
        """Get calendar statistics"""
        events = Event.query.filter_by(calendar_id=calendar_id).all()
        
        today = datetime.now().date()
        today_count = len([e for e in events if e.start_time.date() == today])
        
        upcoming = CalendarService.get_upcoming_events(calendar_id, 30)
        
        conflicts = MeetingConflict.query.filter(
            MeetingConflict.event_id_1.in_([e.event_id for e in events]) |
            MeetingConflict.event_id_2.in_([e.event_id for e in events])
        ).all()
        
        return {
            'total_events': len(events),
            'today_events': today_count,
            'upcoming_events_30days': len(upcoming),
            'total_conflicts': len(conflicts),
            'unresolved_conflicts': len([c for c in conflicts if not c.is_resolved])
        }
