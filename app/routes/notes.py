"""Update Notes Routes"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.note import Note, NoteCategory
from app.services.note_service import NoteService
from app.routes import notes_bp
import json

# ============================================
# CATEGORY MANAGEMENT
# ============================================

@notes_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create a note category"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('category_name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    try:
        category = NoteService.create_category(
            user_id,
            data.get('category_name'),
            data.get('color_code', '#e0e7ff')
        )
        return jsonify({
            'message': 'Category created successfully',
            'category': category_to_dict(category)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('/categories', methods=['GET'])
@jwt_required()
def list_categories():
    """List all categories for user"""
    user_id = get_jwt_identity()
    
    try:
        categories = NoteService.get_user_categories(user_id)
        return jsonify({
            'total': len(categories),
            'categories': [category_to_dict(c) for c in categories]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# NOTE CRUD OPERATIONS
# ============================================

@notes_bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    """Create a new note"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    try:
        note = NoteService.create_note(user_id, data)
        return jsonify({
            'message': 'Note created successfully',
            'note': note_to_dict(note)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('', methods=['GET'])
@jwt_required()
def list_notes():
    """List notes with filters"""
    user_id = get_jwt_identity()
    
    view = request.args.get('view', 'active')  # active, archived, pinned
    category_id = request.args.get('category_id', type=int)
    tag = request.args.get('tag')
    search = request.args.get('search')
    
    try:
        if search:
            notes = NoteService.search_notes(user_id, search)
        elif tag:
            notes = NoteService.get_notes_by_tag(user_id, tag)
        elif category_id:
            notes = NoteService.get_notes_by_category(user_id, category_id)
        elif view == 'archived':
            notes = NoteService.get_user_notes(user_id, archived=True)
        elif view == 'pinned':
            notes = NoteService.get_user_notes(user_id, pinned_only=True)
        else:
            notes = NoteService.get_user_notes(user_id, archived=False)
        
        return jsonify({
            'total': len(notes),
            'notes': [note_to_dict(n) for n in notes]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Get specific note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    return jsonify(note_to_dict(note)), 200

@notes_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """Update a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    data = request.get_json()
    
    try:
        note = NoteService.update_note(note_id, data)
        return jsonify({
            'message': 'Note updated successfully',
            'note': note_to_dict(note)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    try:
        NoteService.delete_note(note_id)
        return jsonify({'message': 'Note deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# NOTE ACTIONS
# ============================================

@notes_bp.route('/<int:note_id>/pin', methods=['POST'])
@jwt_required()
def pin_note(note_id):
    """Pin a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    try:
        note = NoteService.pin_note(note_id)
        return jsonify({
            'message': 'Note pinned',
            'note': note_to_dict(note)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('/<int:note_id>/unpin', methods=['POST'])
@jwt_required()
def unpin_note(note_id):
    """Unpin a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    try:
        note = NoteService.unpin_note(note_id)
        return jsonify({
            'message': 'Note unpinned',
            'note': note_to_dict(note)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('/<int:note_id>/archive', methods=['POST'])
@jwt_required()
def archive_note(note_id):
    """Archive a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    try:
        note = NoteService.archive_note(note_id)
        return jsonify({
            'message': 'Note archived',
            'note': note_to_dict(note)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@notes_bp.route('/<int:note_id>/unarchive', methods=['POST'])
@jwt_required()
def unarchive_note(note_id):
    """Unarchive a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(note_id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    try:
        note = NoteService.unarchive_note(note_id)
        return jsonify({
            'message': 'Note unarchived',
            'note': note_to_dict(note)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# STATISTICS
# ============================================

@notes_bp.route('/statistics/summary', methods=['GET'])
@jwt_required()
def get_note_statistics():
    """Get note statistics"""
    user_id = get_jwt_identity()
    stats = NoteService.get_note_statistics(user_id)
    return jsonify(stats), 200

# ============================================
# HELPER FUNCTIONS
# ============================================

def category_to_dict(category: NoteCategory) -> dict:
    """Convert category to dictionary"""
    return {
        'category_id': category.category_id,
        'category_name': category.category_name,
        'color_code': category.color_code,
        'created_at': category.created_at.isoformat()
    }

def note_to_dict(note: Note) -> dict:
    """Convert note to dictionary"""
    tags = []
    if note.tags:
        try:
            tags = json.loads(note.tags)
        except:
            tags = []
    
    return {
        'note_id': note.note_id,
        'title': note.title,
        'content': note.content,
        'category_id': note.category_id,
        'tags': tags,
        'is_pinned': note.is_pinned,
        'is_archived': note.is_archived,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    }
