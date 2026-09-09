"""Services Routes"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.service import ServiceCategory, ServiceProvider, ServiceReview, ServiceBooking
from app.services.service_service import ServiceDirectoryService
from app.routes import services_bp
from datetime import datetime

# ============================================
# SERVICE CATEGORIES
# ============================================

@services_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get service categories"""
    try:
        categories = ServiceDirectoryService.get_categories()
        return jsonify({
            'total': len(categories),
            'categories': [category_to_dict(c) for c in categories]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# SERVICE PROVIDERS
# ============================================

@services_bp.route('/providers', methods=['GET'])
def search_providers():
    """Search service providers"""
    category_id = request.args.get('category_id', type=int)
    city = request.args.get('city')
    search = request.args.get('search')
    min_rating = request.args.get('min_rating', default=0, type=float)
    
    try:
        providers = ServiceDirectoryService.search_providers(
            category_id, city, search, min_rating
        )
        return jsonify({
            'total': len(providers),
            'providers': [provider_to_dict(p) for p in providers]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/providers/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    """Get provider details"""
    try:
        details = ServiceDirectoryService.get_provider_details(provider_id)
        if not details:
            return jsonify({'error': 'Provider not found'}), 404
        return jsonify(details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# SERVICE REVIEWS
# ============================================

@services_bp.route('/providers/<int:provider_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(provider_id):
    """Add review for provider"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('rating') or not data.get('review_text'):
        return jsonify({'error': 'Rating and review text required'}), 400
    
    try:
        review = ServiceDirectoryService.add_review(
            user_id,
            provider_id,
            data.get('rating'),
            data.get('review_text')
        )
        return jsonify({
            'message': 'Review added',
            'review': review_to_dict(review)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/providers/<int:provider_id>/reviews', methods=['GET'])
def get_provider_reviews(provider_id):
    """Get provider reviews"""
    try:
        reviews = ServiceReview.query.filter_by(provider_id=provider_id).all()
        return jsonify({
            'total': len(reviews),
            'reviews': [review_to_dict(r) for r in reviews]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# SERVICE BOOKINGS
# ============================================

@services_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create service booking"""
    user_id = get_jwt_identity()
    data = request.get_json()
    provider_id = data.get('provider_id')
    
    if not provider_id:
        return jsonify({'error': 'Provider ID required'}), 400
    
    try:
        booking = ServiceDirectoryService.book_service(user_id, provider_id, data)
        return jsonify({
            'message': 'Booking created',
            'booking': booking_to_dict(booking)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_bookings():
    """List user bookings"""
    user_id = get_jwt_identity()
    status = request.args.get('status')
    
    try:
        bookings = ServiceDirectoryService.get_user_bookings(user_id, status)
        return jsonify({
            'total': len(bookings),
            'bookings': [booking_to_dict(b) for b in bookings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@services_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get booking details"""
    user_id = get_jwt_identity()
    booking = ServiceBooking.query.filter_by(booking_id=booking_id, user_id=user_id).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify(booking_to_dict(booking)), 200

@services_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    """Update booking status"""
    user_id = get_jwt_identity()
    booking = ServiceBooking.query.filter_by(booking_id=booking_id, user_id=user_id).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    data = request.get_json()
    status = data.get('status')
    
    try:
        booking = ServiceDirectoryService.update_booking_status(booking_id, status)
        return jsonify({
            'message': 'Booking status updated',
            'booking': booking_to_dict(booking)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# STATISTICS
# ============================================

@services_bp.route('/statistics/summary', methods=['GET'])
@jwt_required()
def get_booking_stats():
    """Get booking statistics"""
    user_id = get_jwt_identity()
    stats = ServiceDirectoryService.get_booking_statistics(user_id)
    return jsonify(stats), 200

# ============================================
# HELPER FUNCTIONS
# ============================================

def category_to_dict(category: ServiceCategory) -> dict:
    return {
        'category_id': category.service_category_id,
        'category_name': category.category_name,
        'description': category.description,
        'icon_name': category.icon_name
    }

def provider_to_dict(provider: ServiceProvider) -> dict:
    return {
        'provider_id': provider.provider_id,
        'business_name': provider.business_name,
        'category_id': provider.category_id,
        'description': provider.description,
        'phone': provider.phone_number,
        'email': provider.email,
        'website': provider.website,
        'address': provider.address,
        'city': provider.city,
        'state': provider.state,
        'postal_code': provider.postal_code,
        'average_rating': float(provider.average_rating),
        'total_reviews': provider.total_reviews,
        'price_range': provider.price_range,
        'availability_status': provider.availability_status
    }

def review_to_dict(review: ServiceReview) -> dict:
    return {
        'review_id': review.review_id,
        'provider_id': review.provider_id,
        'rating': review.rating,
        'review_text': review.review_text,
        'review_date': review.review_date.isoformat(),
        'helpful_count': review.helpful_count
    }

def booking_to_dict(booking: ServiceBooking) -> dict:
    return {
        'booking_id': booking.booking_id,
        'provider_id': booking.provider_id,
        'booking_date': booking.booking_date.isoformat(),
        'booking_time': booking.booking_time.isoformat() if booking.booking_time else None,
        'service_type': booking.service_type,
        'duration_minutes': booking.duration_minutes,
        'notes': booking.notes,
        'status': booking.status,
        'cost': float(booking.cost),
        'payment_status': booking.payment_status,
        'created_at': booking.created_at.isoformat()
    }
