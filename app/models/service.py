"""Service Models"""
from app import db
from datetime import datetime

class ServiceCategory(db.Model):
    """Service category model"""
    __tablename__ = 'service_categories'
    
    service_category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceProvider(db.Model):
    """Service provider model"""
    __tablename__ = 'service_providers'
    
    provider_id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.service_category_id'), nullable=False)
    description = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(150))
    website = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    average_rating = db.Column(db.Numeric(3, 2), default=0)
    total_reviews = db.Column(db.Integer, default=0)
    price_range = db.Column(db.String(50))
    business_hours = db.Column(db.Text)  # JSON
    availability_status = db.Column(db.String(50), default='available')
    service_area = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ServiceReview(db.Model):
    """Service review model"""
    __tablename__ = 'service_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_providers.provider_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    review_date = db.Column(db.Date, nullable=False)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ServiceBooking(db.Model):
    """Service booking model"""
    __tablename__ = 'service_bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_providers.provider_id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time)
    service_type = db.Column(db.String(100))
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    cost = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.String(50), default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
