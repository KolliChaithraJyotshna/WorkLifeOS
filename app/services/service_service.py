"""Service Service - Business Logic for Local Services"""
from app import db
from app.models.service import ServiceCategory, ServiceProvider, ServiceReview, ServiceBooking
from datetime import datetime, date
from sqlalchemy import and_, func
from decimal import Decimal

class ServiceDirectoryService:
    """Service for local services operations"""
    
    @staticmethod
    def create_category(category_name: str, description: str = '', icon_name: str = '') -> ServiceCategory:
        """Create service category"""
        category = ServiceCategory(
            category_name=category_name,
            description=description,
            icon_name=icon_name
        )
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def get_categories() -> list:
        """Get all service categories"""
        return ServiceCategory.query.all()
    
    @staticmethod
    def create_provider(data: dict) -> ServiceProvider:
        """Create service provider"""
        provider = ServiceProvider(
            business_name=data.get('business_name'),
            category_id=data.get('category_id'),
            description=data.get('description'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            website=data.get('website'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            price_range=data.get('price_range'),
            business_hours=data.get('business_hours'),
            availability_status=data.get('availability_status', 'available'),
            service_area=data.get('service_area')
        )
        db.session.add(provider)
        db.session.commit()
        return provider
    
    @staticmethod
    def search_providers(category_id: int = None, city: str = None,
                        search_term: str = None, min_rating: float = 0) -> list:
        """Search for service providers"""
        query = ServiceProvider.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if city:
            query = query.filter_by(city=city)
        if search_term:
            query = query.filter(
                ServiceProvider.business_name.ilike(f'%{search_term}%') |
                ServiceProvider.description.ilike(f'%{search_term}%')
            )
        if min_rating > 0:
            query = query.filter(ServiceProvider.average_rating >= min_rating)
        
        return query.order_by(ServiceProvider.average_rating.desc()).all()
    
    @staticmethod
    def get_provider_details(provider_id: int) -> dict:
        """Get provider with reviews and details"""
        provider = ServiceProvider.query.get(provider_id)
        if not provider:
            return None
        
        reviews = ServiceReview.query.filter_by(provider_id=provider_id).all()
        
        return {
            'provider': provider,
            'reviews': reviews,
            'review_count': len(reviews),
            'average_rating': provider.average_rating
        }
    
    @staticmethod
    def add_review(user_id: int, provider_id: int, rating: int, review_text: str) -> ServiceReview:
        """Add review for provider"""
        review = ServiceReview(
            provider_id=provider_id,
            user_id=user_id,
            rating=rating,
            review_text=review_text,
            review_date=date.today()
        )
        db.session.add(review)
        
        # Update provider rating
        ServiceDirectoryService.update_provider_rating(provider_id)
        
        db.session.commit()
        return review
    
    @staticmethod
    def update_provider_rating(provider_id: int):
        """Recalculate provider rating based on reviews"""
        reviews = ServiceReview.query.filter_by(provider_id=provider_id).all()
        provider = ServiceProvider.query.get(provider_id)
        
        if reviews:
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)
            provider.average_rating = Decimal(str(round(avg_rating, 2)))
            provider.total_reviews = len(reviews)
        
        db.session.commit()
    
    @staticmethod
    def book_service(user_id: int, provider_id: int, data: dict) -> ServiceBooking:
        """Create service booking"""
        booking = ServiceBooking(
            user_id=user_id,
            provider_id=provider_id,
            booking_date=datetime.strptime(data.get('booking_date'), '%Y-%m-%d').date(),
            booking_time=data.get('booking_time'),
            service_type=data.get('service_type'),
            duration_minutes=data.get('duration_minutes'),
            notes=data.get('notes'),
            status=data.get('status', 'pending'),
            cost=Decimal(str(data.get('cost', 0))),
            payment_status=data.get('payment_status', 'unpaid')
        )
        db.session.add(booking)
        db.session.commit()
        return booking
    
    @staticmethod
    def get_user_bookings(user_id: int, status: str = None) -> list:
        """Get bookings for user"""
        query = ServiceBooking.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(ServiceBooking.booking_date.desc()).all()
    
    @staticmethod
    def update_booking_status(booking_id: int, status: str) -> ServiceBooking:
        """Update booking status"""
        booking = ServiceBooking.query.get(booking_id)
        if booking:
            booking.status = status
            booking.updated_at = datetime.utcnow()
            db.session.commit()
        return booking
    
    @staticmethod
    def update_booking_payment(booking_id: int, payment_status: str) -> ServiceBooking:
        """Update booking payment status"""
        booking = ServiceBooking.query.get(booking_id)
        if booking:
            booking.payment_status = payment_status
            booking.updated_at = datetime.utcnow()
            db.session.commit()
        return booking
    
    @staticmethod
    def get_booking_statistics(user_id: int) -> dict:
        """Get booking statistics for user"""
        bookings = ServiceBooking.query.filter_by(user_id=user_id).all()
        
        completed = len([b for b in bookings if b.status == 'completed'])
        pending = len([b for b in bookings if b.status == 'pending'])
        confirmed = len([b for b in bookings if b.status == 'confirmed'])
        cancelled = len([b for b in bookings if b.status == 'cancelled'])
        
        total_spent = float(sum([b.cost for b in bookings if b.status == 'completed']))
        
        return {
            'total_bookings': len(bookings),
            'completed': completed,
            'pending': pending,
            'confirmed': confirmed,
            'cancelled': cancelled,
            'total_spent': total_spent
        }
