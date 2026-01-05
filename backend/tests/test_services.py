import pytest

from unittest.mock import patch, MagicMock
from app.services import get_mpesa_access_token, stk_push


@pytest.fixture
def mock_business_keys():
    # A mock object that mimics the APIKeys model
    mock_keys = MagicMock()
    mock_keys.consumer_key = 'mock_consumer_key'
    mock_keys.consumer_secret = 'mock_consumer_secret'
    mock_keys.till_number = '12345'
    mock_keys.paybill_number = None
    return mock_keys

@patch('requests.get')
def test_get_mpesa_access_token_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'access_token': 'mock_access_token'}
    mock_get.return_value = mock_response

    token = get_mpesa_access_token('key', 'secret')
    assert token == 'mock_access_token'
    mock_get.assert_called_once()

@patch('requests.get')
def test_get_mpesa_access_token_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_get.return_value = mock_response

    token = get_mpesa_access_token('key', 'secret')
    assert token is None
    mock_get.assert_called_once()

@patch('app.services.get_mpesa_access_token')
@patch('requests.post')
def test_stk_push_success_till(mock_post, mock_get_token, app, mock_business_keys):
    mock_get_token.return_value = 'mock_access_token'
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {
        "ResponseCode": "0",
        "CheckoutRequestID": "ws_CO_05012026123456789",
        "CustomerMessage": "Success. Request accepted for processing"
    }
    mock_post.return_value = mock_post_response

    with app.app_context():
        result = stk_push('254712345678', 10, mock_business_keys)

    assert result['ResponseCode'] == "0"
    assert result['CheckoutRequestID'] == "ws_CO_05012026123456789"
    mock_get_token.assert_called_once()
    mock_post.assert_called_once()
    
@patch('app.services.get_mpesa_access_token')
@patch('requests.post')
def test_stk_push_success_paybill(mock_post, mock_get_token, app, mock_business_keys):
    mock_business_keys.till_number = None
    mock_business_keys.paybill_number = '600123' # Set paybill number
    mock_get_token.return_value = 'mock_access_token'
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {
        "ResponseCode": "0",
        "CheckoutRequestID": "ws_CO_05012026123456789",
        "CustomerMessage": "Success. Request accepted for processing"
    }
    mock_post.return_value = mock_post_response

    with app.app_context():
        result = stk_push('254712345678', 10, mock_business_keys)

    assert result['ResponseCode'] == "0"
    assert result['CheckoutRequestID'] == "ws_CO_05012026123456789"
    mock_get_token.assert_called_once()
    mock_post.assert_called_once()

@patch('app.services.get_mpesa_access_token')
@patch('requests.post')
def test_stk_push_no_access_token(mock_post, mock_get_token, app, mock_business_keys):
    mock_get_token.return_value = None # Simulate no access token
    
    with app.app_context():
        result = stk_push('254712345678', 10, mock_business_keys)

    assert result is None
    mock_get_token.assert_called_once()
    mock_post.assert_not_called()

@patch('app.services.get_mpesa_access_token')
@patch('requests.post')
def test_stk_push_mpesa_api_failure(mock_post, mock_get_token, app, mock_business_keys):
    mock_get_token.return_value = 'mock_access_token'
    mock_post_response = MagicMock()
    mock_post_response.status_code = 400
    mock_post_response.text = 'M-Pesa error details'
    mock_post.return_value = mock_post_response

    with app.app_context():
        result = stk_push('254712345678', 10, mock_business_keys)

    assert result is None
    mock_get_token.assert_called_once()
    mock_post.assert_called_once()

@patch('app.services.get_mpesa_access_token')
@patch('requests.post')
def test_stk_push_no_shortcode_configured(mock_post, mock_get_token, app):
    mock_keys = MagicMock()
    mock_keys.consumer_key = 'mock_consumer_key'
    mock_keys.consumer_secret = 'mock_consumer_secret'
    mock_keys.till_number = None
    mock_keys.paybill_number = None
    
    with app.app_context():
        result = stk_push('254712345678', 10, mock_keys)

    assert result is None
    mock_get_token.assert_not_called()
    mock_post.assert_not_called()
