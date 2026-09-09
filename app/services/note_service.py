"""Note Service - Business Logic"""
from app import db
from app.models.note import Note, NoteCategory, NoteAttachment
from datetime import datetime
from sqlalchemy import or_
import json

class NoteService:
    """Service for note operations"""
    
    @staticmethod
    def create_category(user_id: int, category_name: str, color_code: str = '#e0e7ff') -> NoteCategory:
        """Create a note category"""
        category = NoteCategory(
            user_id=user_id,
            category_name=category_name,
            color_code=color_code
        )
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def get_user_categories(user_id: int) -> list:
        """Get all categories for user"""
        return NoteCategory.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def create_note(user_id: int, data: dict) -> Note:
        """Create a new note"""
        tags = data.get('tags', [])
        if isinstance(tags, list):
            tags = json.dumps(tags)
        
        note = Note(
            user_id=user_id,
            title=data.get('title'),
            content=data.get('content'),
            category_id=data.get('category_id'),
            tags=tags,
            is_pinned=data.get('is_pinned', False),
            is_archived=data.get('is_archived', False)
        )
        db.session.add(note)
        db.session.commit()
        return note
    
    @staticmethod
    def update_note(note_id: int, data: dict) -> Note:
        """Update a note"""
        note = Note.query.get(note_id)
        if not note:
            return None
        
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']
        if 'category_id' in data:
            note.category_id = data['category_id']
        if 'tags' in data:
            tags = data['tags']
            if isinstance(tags, list):
                tags = json.dumps(tags)
            note.tags = tags
        if 'is_pinned' in data:
            note.is_pinned = data['is_pinned']
        if 'is_archived' in data:
            note.is_archived = data['is_archived']
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        return note
    
    @staticmethod
    def get_user_notes(user_id: int, archived: bool = False, pinned_only: bool = False) -> list:
        """Get notes for user"""
        query = Note.query.filter_by(user_id=user_id, is_archived=archived)
        
        if pinned_only:
            query = query.filter_by(is_pinned=True)
        
        return query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
    
    @staticmethod
    def search_notes(user_id: int, search_term: str) -> list:
        """Search notes by title or content"""
        return Note.query.filter(
            Note.user_id == user_id,
            or_(
                Note.title.ilike(f'%{search_term}%'),
                Note.content.ilike(f'%{search_term}%')
            )
        ).all()
    
    @staticmethod
    def get_notes_by_tag(user_id: int, tag: str) -> list:
        """Get notes by tag"""
        notes = Note.query.filter_by(user_id=user_id).all()
        return [
            n for n in notes
            if n.tags and tag in json.loads(n.tags)
        ]
    
    @staticmethod
    def get_notes_by_category(user_id: int, category_id: int) -> list:
        """Get notes by category"""
        return Note.query.filter_by(user_id=user_id, category_id=category_id).all()
    
    @staticmethod
    def pin_note(note_id: int) -> Note:
        """Pin a note"""
        note = Note.query.get(note_id)
        if note:
            note.is_pinned = True
            note.updated_at = datetime.utcnow()
            db.session.commit()
        return note
    
    @staticmethod
    def unpin_note(note_id: int) -> Note:
        """Unpin a note"""
        note = Note.query.get(note_id)
        if note:
            note.is_pinned = False
            note.updated_at = datetime.utcnow()
            db.session.commit()
        return note
    
    @staticmethod
    def archive_note(note_id: int) -> Note:
        """Archive a note"""
        note = Note.query.get(note_id)
        if note:
            note.is_archived = True
            note.updated_at = datetime.utcnow()
            db.session.commit()
        return note
    
    @staticmethod
    def unarchive_note(note_id: int) -> Note:
        """Unarchive a note"""
        note = Note.query.get(note_id)
        if note:
            note.is_archived = False
            note.updated_at = datetime.utcnow()
            db.session.commit()
        return note
    
    @staticmethod
    def delete_note(note_id: int) -> bool:
        """Delete a note"""
        note = Note.query.get(note_id)
        if not note:
            return False
        db.session.delete(note)
        db.session.commit()
        return True
    
    @staticmethod
    def add_attachment(note_id: int, filename: str, filepath: str, file_type: str, file_size: int) -> NoteAttachment:
        """Add attachment to note"""
        attachment = NoteAttachment(
            note_id=note_id,
            file_name=filename,
            file_path=filepath,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(attachment)
        db.session.commit()
        return attachment
    
    @staticmethod
    def get_note_statistics(user_id: int) -> dict:
        """Get note statistics"""
        notes = Note.query.filter_by(user_id=user_id).all()
        active_notes = [n for n in notes if not n.is_archived]
        archived_notes = [n for n in notes if n.is_archived]
        pinned_notes = [n for n in notes if n.is_pinned]
        
        return {
            'total_notes': len(notes),
            'active_notes': len(active_notes),
            'archived_notes': len(archived_notes),
            'pinned_notes': len(pinned_notes),
            'total_attachments': sum([a.count() for a in [n.attachments for n in notes]])
        }
