#!/usr/bin/env python
"""WorkLifeOS Application Entry Point"""
import os
from app import create_app, db
from app.models import (
    User, Calendar, Event, MeetingConflict,
    Task, TaskDependency, TaskHistory,
    NoteCategory, Note, NoteAttachment,
    ExpenseCategory, Expense, Invoice, InvoiceItem,
    Habit, HabitLog, HabitStreak,
    ServiceCategory, ServiceProvider, ServiceReview, ServiceBooking
)

if __name__ == '__main__':
    config = os.getenv('FLASK_ENV', 'development')
    app = create_app(config)
    
    @app.shell_context_processor
    def make_shell_context():
        """Add models to shell context"""
        return {
            'db': db,
            'User': User,
            'Calendar': Calendar,
            'Event': Event,
            'Task': Task,
            'Note': Note,
            'Expense': Expense,
            'Habit': Habit,
            'ServiceProvider': ServiceProvider,
            'ServiceBooking': ServiceBooking
        }
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=(config == 'development')
    )
