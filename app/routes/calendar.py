"""Calendar Routes"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.calendar import Calendar, Event, MeetingConflict
from app.services.calendar_service import CalendarService
from app.routes import calendar_bp
from datetime import datetime

# ============================================
# CALENDAR MANAGEMENT
# ============================================

@calendar_bp.route('', methods=['POST'])
@jwt_required()
def create_calendar():
    """Create a new calendar"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('calendar_name'):
        return jsonify({'error': 'Calendar name is required'}), 400
    
    try:
        calendar = CalendarService.create_calendar(
            user_id,
            data.get('calendar_name'),
            data.get('color_code', '#3b82f6'),
            data.get('is_primary', False)
        )
        return jsonify({
            'message': 'Calendar created successfully',
            'calendar': calendar_to_dict(calendar)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('', methods=['GET'])
@jwt_required()
def list_calendars():
    """List all calendars for user"""
    user_id = get_jwt_identity()
    
    try:
        calendars = CalendarService.get_user_calendars(user_id)
        return jsonify({
            'total': len(calendars),
            'calendars': [calendar_to_dict(c) for c in calendars]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/<int:calendar_id>', methods=['GET'])
@jwt_required()
def get_calendar(calendar_id):
    """Get calendar details"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    stats = CalendarService.get_calendar_statistics(calendar_id)
    result = calendar_to_dict(calendar)
    result['statistics'] = stats
    
    return jsonify(result), 200

# ============================================
# EVENT MANAGEMENT
# ============================================

@calendar_bp.route('/<int:calendar_id>/events', methods=['POST'])
@jwt_required()
def create_event(calendar_id):
    """Create a new event"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    data = request.get_json()
    
    # Validation
    if not data or not data.get('title'):
        return jsonify({'error': 'Event title is required'}), 400
    if not data.get('start_time') or not data.get('end_time'):
        return jsonify({'error': 'Start time and end time are required'}), 400
    
    try:
        event = CalendarService.create_event(calendar_id, data)
        return jsonify({
            'message': 'Event created successfully',
            'event': event_to_dict(event)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """Get event details"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Verify calendar belongs to user
    calendar = event.calendar
    if calendar.user_id != get_jwt_identity():
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(event_to_dict(event)), 200

@calendar_bp.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update an event"""
    user_id = get_jwt_identity()
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Verify calendar belongs to user
    if event.calendar.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        event = CalendarService.update_event(event_id, data)
        return jsonify({
            'message': 'Event updated successfully',
            'event': event_to_dict(event)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """Delete an event"""
    user_id = get_jwt_identity()
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event.calendar.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        CalendarService.delete_event(event_id)
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# EVENT FILTERING
# ============================================

@calendar_bp.route('/<int:calendar_id>/events/date/<string:event_date>', methods=['GET'])
@jwt_required()
def get_events_by_date(calendar_id, event_date):
    """Get events for a specific date"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    try:
        events = CalendarService.get_events_by_date(calendar_id, event_date)
        return jsonify({
            'date': event_date,
            'total': len(events),
            'events': [event_to_dict(e) for e in events]
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/<int:calendar_id>/events/range', methods=['GET'])
@jwt_required()
def get_events_by_range(calendar_id):
    """Get events within a date range"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start and end parameters are required'}), 400
    
    try:
        events = CalendarService.get_events_by_range(calendar_id, start_date, end_date)
        return jsonify({
            'start': start_date,
            'end': end_date,
            'total': len(events),
            'events': [event_to_dict(e) for e in events]
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/<int:calendar_id>/events/today', methods=['GET'])
@jwt_required()
def get_today_events(calendar_id):
    """Get today's events"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    try:
        events = CalendarService.get_today_events(calendar_id)
        return jsonify({
            'total': len(events),
            'events': [event_to_dict(e) for e in events]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/<int:calendar_id>/events/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_events(calendar_id):
    """Get upcoming events"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    days = request.args.get('days', default=7, type=int)
    
    try:
        events = CalendarService.get_upcoming_events(calendar_id, days)
        return jsonify({
            'days': days,
            'total': len(events),
            'events': [event_to_dict(e) for e in events]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# CONFLICT MANAGEMENT
# ============================================

@calendar_bp.route('/<int:calendar_id>/conflicts', methods=['GET'])
@jwt_required()
def get_conflicts(calendar_id):
    """Get conflicts for calendar user"""
    user_id = get_jwt_identity()
    calendar = Calendar.query.filter_by(calendar_id=calendar_id, user_id=user_id).first()
    
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    resolved = request.args.get('resolved', default='false').lower() == 'true'
    
    try:
        conflicts = CalendarService.get_conflicts_for_user(user_id, resolved)
        return jsonify({
            'total': len(conflicts),
            'conflicts': [conflict_to_dict(c) for c in conflicts]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/conflicts/<int:conflict_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_conflict(conflict_id):
    """Mark conflict as resolved"""
    user_id = get_jwt_identity()
    conflict = MeetingConflict.query.get(conflict_id)
    
    if not conflict or conflict.user_id != user_id:
        return jsonify({'error': 'Conflict not found'}), 404
    
    data = request.get_json() or {}
    resolution_note = data.get('resolution_note', '')
    
    try:
        CalendarService.resolve_conflict(conflict_id, resolution_note)
        return jsonify({
            'message': 'Conflict marked as resolved',
            'conflict': conflict_to_dict(conflict)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# HELPER FUNCTIONS
# ============================================

def calendar_to_dict(calendar: Calendar) -> dict:
    """Convert calendar to dictionary"""
    return {
        'calendar_id': calendar.calendar_id,
        'calendar_name': calendar.calendar_name,
        'color_code': calendar.color_code,
        'is_primary': calendar.is_primary,
        'created_at': calendar.created_at.isoformat()
    }

def event_to_dict(event: Event) -> dict:
    """Convert event to dictionary"""
    return {
        'event_id': event.event_id,
        'calendar_id': event.calendar_id,
        'title': event.title,
        'description': event.description,
        'start_time': event.start_time.isoformat(),
        'end_time': event.end_time.isoformat(),
        'location': event.location,
        'timezone': event.timezone,
        'event_type': event.event_type,
        'attendees': event.attendees,
        'reminder_minutes': event.reminder_minutes,
        'is_recurring': event.is_recurring,
        'recurrence_pattern': event.recurrence_pattern,
        'created_at': event.created_at.isoformat(),
        'updated_at': event.updated_at.isoformat()
    }

def conflict_to_dict(conflict: MeetingConflict) -> dict:
    """Convert conflict to dictionary"""
    return {
        'conflict_id': conflict.conflict_id,
        'event_id_1': conflict.event_id_1,
        'event_id_2': conflict.event_id_2,
        'conflict_type': conflict.conflict_type,
        'detected_at': conflict.detected_at.isoformat(),
        'is_resolved': conflict.is_resolved,
        'resolution_note': conflict.resolution_note
    }
