from . import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    api_keys = db.relationship('APIKeys', backref='business', lazy=True, uselist=False)
    transactions = db.relationship('Transaction', backref='business', lazy=True)
    customers = db.relationship('Customer', backref='business', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class APIKeys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumer_key = db.Column(db.String(255), nullable=False)
    consumer_secret = db.Column(db.String(255), nullable=False)
    till_number = db.Column(db.String(20))
    paybill_number = db.Column(db.String(20))
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    checkout_request_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    phone_number = db.Column(db.String(20), nullable=False)
    total_amount_requested = db.Column(db.Float, default=0)
    transaction_count = db.Column(db.Integer, default=0)
    last_transaction_date = db.Column(db.DateTime)
    first_transaction_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='customer', lazy=True)

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
