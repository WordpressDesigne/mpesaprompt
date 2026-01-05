import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from backend.app import create_app, db
from backend.app.models import Business, AdminUser, APIKeys, Transaction, Customer, Wallet, CommissionLedger
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def app():
    # Use a test configuration
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
        'MPESA_PASSKEY': 'test_passkey',
        'MPESA_CALLBACK_URL': 'http://test.com/callback'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def auth_client(client, app):
    with app.app_context():
        # Create a test business user
        business_user = Business(name='Test Business', email='test@business.com')
        business_user.set_password('password')
        db.session.add(business_user)
        db.session.commit()

        # Log in the business user
        res = client.post('/login', json={'email': 'test@business.com', 'password': 'password'})
        token = res.json['access_token']

    # Return a client with the auth header
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return client

@pytest.fixture(scope='function')
def admin_auth_client(client, app):
    with app.app_context():
        # Create a test admin user
        admin_user = AdminUser(email='admin@mpesa.com')
        admin_user.set_password('adminpassword')
        db.session.add(admin_user)
        db.session.commit()

        # Log in the admin user
        res = client.post('/admin/login', json={'email': 'admin@mpesa.com', 'password': 'adminpassword'})
        token = res.json['access_token']

    # Return a client with the auth header
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return client

@pytest.fixture(scope='function')
def new_business_with_keys(app):
    with app.app_context():
        business = Business(name='Keyed Business', email='keyed@business.com')
        business.set_password('password')
        db.session.add(business)
        db.session.commit()

        api_keys = APIKeys(
            consumer_key='test_consumer_key',
            consumer_secret='test_consumer_secret',
            till_number='12345',
            paybill_number=None,
            business_id=business.id
        )
        db.session.add(api_keys)
        db.session.commit()
        return business
