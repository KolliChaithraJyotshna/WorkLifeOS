"""Update services module to include all services"""
from app.services.task_service import TaskService
from app.services.calendar_service import CalendarService
from app.services.note_service import NoteService
from app.services.expense_service import ExpenseService
from app.services.habit_service import HabitService
from app.services.service_service import ServiceDirectoryService

__all__ = [
    'TaskService',
    'CalendarService',
    'NoteService',
    'ExpenseService',
    'HabitService',
    'ServiceDirectoryService'
]
