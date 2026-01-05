import pytest
from backend.app import models
from unittest.mock import patch, MagicMock
from app import db

from flask_jwt_extended import create_access_token
import datetime

@patch('app.routes.stk_push')
def test_send_stk_push_success(mock_stk_push, app, client, new_business_with_keys):
    # Mock stk_push service to return success
    mock_stk_push.return_value = {
        "ResponseCode": "0",
        "CheckoutRequestID": "ws_CO_05012026123456789",
        "CustomerMessage": "Success. Request accepted for processing"
    }

    with app.app_context():
        # Get a token for the new business
        business = new_business_with_keys
        access_token = create_access_token(identity=f"business_{business.id}")

        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        response = client.post(
            '/stk-push', 
            headers=headers, 
            json={'phone_number': '254712345678', 'amount': 10}
        )
        assert response.status_code == 200
        assert 'STK push sent successfully' in response.json['message']
        assert 'checkout_request_id' in response.json

        # Verify transaction was logged
        transaction = models.Transaction.query.filter_by(checkout_request_id="ws_CO_05012026123456789").first()
        assert transaction is not None
        assert transaction.status == 'pending'
        assert transaction.amount == 10
        assert transaction.phone_number == '254712345678'
        mock_stk_push.assert_called_once()

@patch('app.routes.stk_push')
def test_send_stk_push_no_api_keys(mock_stk_push, app, client):
    with app.app_context():
        business = models.Business(name='No Keys models.Business', email='nokey@business.com')
        business.set_password('password')
        db.session.add(business)
        db.session.commit()
        access_token = create_access_token(identity=f"business_{business.id}")

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    response = client.post(
        '/stk-push', 
        headers=headers, 
        json={'phone_number': '254712345678', 'amount': 10}
    )
    assert response.status_code == 400
    assert 'M-Pesa API keys are not configured' in response.json['message']
    mock_stk_push.assert_not_called()

@patch('app.routes.stk_push')
def test_send_stk_push_mpesa_failure(mock_stk_push, app, client, new_business_with_keys):
    mock_stk_push.return_value = {
        "ResponseCode": "1", # Simulate M-Pesa failure
        "CheckoutRequestID": "ws_CO_05012026123456790",
        "CustomerMessage": "Failed to process the request"
    }
    with app.app_context():
        business = new_business_with_keys
        access_token = create_access_token(identity=f"business_{business.id}")

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    response = client.post(
        '/stk-push', 
        headers=headers, 
        json={'phone_number': '254712345678', 'amount': 10}
    )
    assert response.status_code == 400
    assert 'STK push failed' in response.json['message']
    mock_stk_push.assert_called_once()

def test_callback_success(app, client, new_business_with_keys):
    with app.app_context():
        business = new_business_with_keys
        # Create a pending transaction
        transaction = models.Transaction(
            amount=10, 
            phone_number='254712345678', 
            checkout_request_id='ws_CO_CALLBACK_TEST', 
            business_id=business.id
        )
        db.session.add(transaction)
        db.session.commit()
        
        initial_balance = business.wallet.balance if business.wallet else 0.0

    callback_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29199-633004-1",
                "CheckoutRequestID": "ws_CO_CALLBACK_TEST",
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 10.0},
                        {"Name": "MpesaReceiptNumber", "Value": "RTP123ABC"},
                        {"Name": "models.TransactionDate", "Value": "20231024100000"},
                        {"Name": "PhoneNumber", "Value": 254712345678}
                    ]
                }
            }
        }
    }
    response = client.post('/callback', json=callback_payload)
    assert response.status_code == 200
    assert 'Callback received' in response.json['message']

    with app.app_context():
        updated_transaction = models.Transaction.query.filter_by(checkout_request_id='ws_CO_CALLBACK_TEST').first()
        assert updated_transaction.status == 'success'
        
        # Verify customer update
        customer = models.Transaction.query.filter_by(checkout_request_id='ws_CO_CALLBACK_TEST').first().customer
        assert customer is not None
        assert customer.total_amount_requested == 10
        assert customer.transaction_count == 1

        # Verify commission deduction
        updated_business = models.Business.query.get(business.id)
        assert updated_business.wallet.balance < initial_balance
        assert updated_business.wallet.balance == pytest.approx(initial_balance - (10 * 0.01))

def test_callback_failure(app, client):
    with app.app_context():
        business = models.Business(name='Fail Test models.Business', email='fail@business.com')
        business.set_password('password')
        db.session.add(business)
        db.session.commit()

        # Create a pending transaction
        transaction = models.Transaction(
            amount=10, 
            phone_number='254712345678', 
            checkout_request_id='ws_CO_CALLBACK_FAIL', 
            business_id=business.id
        )
        db.session.add(transaction)
        db.session.commit()

    callback_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29199-633004-1",
                "CheckoutRequestID": "ws_CO_CALLBACK_FAIL",
                "ResultCode": 1032, # Simulate user cancellation
                "ResultDesc": "User cancelled the request",
                "CallbackMetadata": {} # No metadata for cancelled
            }
        }
    }
    response = client.post('/callback', json=callback_payload)
    assert response.status_code == 200
    assert 'Callback received' in response.json['message']

    with app.app_context():
        updated_transaction = models.Transaction.query.filter_by(checkout_request_id='ws_CO_CALLBACK_FAIL').first()
        assert updated_transaction.status == 'failed'

def test_get_transaction_status_success(app, client, new_business_with_keys):
    with app.app_context():
        business = new_business_with_keys
        access_token = create_access_token(identity=f"business_{business.id}")
        
        # Create a pending transaction
        transaction = models.Transaction(
            amount=5, 
            phone_number='254799999999', 
            checkout_request_id='ws_CO_STATUS_TEST', 
            business_id=business.id
        )
        db.session.add(transaction)
        db.session.commit()

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/transaction-status/ws_CO_STATUS_TEST', headers=headers)
    assert response.status_code == 200
    assert response.json['status'] == 'pending'

def test_get_transaction_status_not_found(app, client, auth_client):
    headers = auth_client.environ_base # Use headers from auth_client fixture
    response = client.get('/transaction-status/NON_EXISTENT_ID', headers=headers)
    assert response.status_code == 404
    assert 'models.Transaction not found' in response.json['message']

def test_get_transaction_status_unauthorized_business(app, client, auth_client, new_business_with_keys):
    with app.app_context():
        # Create a transaction for new_business_with_keys
        business_owner = new_business_with_keys
        transaction = models.Transaction(
            amount=5, 
            phone_number='254799999998', 
            checkout_request_id='ws_CO_OTHER_BUSINESS_TXN', 
            business_id=business_owner.id
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Get token for a different business (from auth_client fixture)
        # auth_client creates a models.Business with email 'test@business.com'
        test_business = models.Business.query.filter_by(email='test@business.com').first()
        access_token_other_business = create_access_token(identity=f"business_{test_business.id}")

    headers = {'Authorization': f'Bearer {access_token_other_business}'}
    response = client.get('/transaction-status/ws_CO_OTHER_BUSINESS_TXN', headers=headers)
    assert response.status_code == 404
    assert 'models.Transaction not found or does not belong to this business' in response.json['message']

def test_get_transaction_status_unauthenticated(client):
    response = client.get('/transaction-status/ANY_ID')
    assert response.status_code == 401 # Unauthorized
