from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# Association table for the many-to-many relationship between users and businesses
business_users = db.Table('business_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('business_id', db.Integer, db.ForeignKey('business.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone_number = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    businesses = db.relationship('Business', secondary=business_users, lazy='subquery',
                               backref=db.backref('users', lazy=True))
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Business(db.Model):
    """Business model representing a tenant in the multi-tenant system."""
    __tablename__ = 'business'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # M-Pesa API credentials
    mpesa_consumer_key = db.Column(db.String(200))
    mpesa_consumer_secret = db.Column(db.String(200))
    mpesa_business_shortcode = db.Column(db.String(20))
    mpesa_passkey = db.Column(db.String(200))
    mpesa_callback_url = db.Column(db.String(200))
    mpesa_environment = db.Column(db.String(20), default='sandbox')
    
    # Relationships
    wallet = db.relationship('Wallet', backref='business', uselist=False, lazy=True)
    transactions = db.relationship('Transaction', backref='business', lazy=True)
    customers = db.relationship('Customer', backref='business', lazy=True)
    
    def __repr__(self):
        return f'<Business {self.name}>'

class Customer(db.Model):
    """Customer model to store customer information for each business."""
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    total_transactions = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Float, default=0.0)
    first_transaction = db.Column(db.DateTime)
    last_transaction = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.phone_number}>'

class Transaction(db.Model):
    """Transaction model to store M-Pesa transaction details."""
    __tablename__ = 'transaction'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, index=True)
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    account_reference = db.Column(db.String(50))
    transaction_desc = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    result_code = db.Column(db.String(10))
    result_desc = db.Column(db.String(255))
    mpesa_receipt_number = db.Column(db.String(50))
    transaction_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Commission related fields
    commission_rate = db.Column(db.Float, default=0.01)  # 1% commission
    commission_amount = db.Column(db.Float, default=0.0)
    
    # Foreign Keys
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id} - {self.amount}>'

class Wallet(db.Model):
    """Wallet model to track business balances and commissions."""
    __tablename__ = 'wallet'
    
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    total_earnings = db.Column(db.Float, default=0.0)
    total_commissions = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='KES')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Wallet {self.business.name} - {self.balance} {self.currency}>'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))
