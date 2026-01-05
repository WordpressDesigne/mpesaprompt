import requests
from flask import current_app
import datetime
import base64

def get_mpesa_access_token(consumer_key, consumer_secret):
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def stk_push(phone_number, amount, business_keys):
    consumer_key = business_keys.consumer_key
    consumer_secret = business_keys.consumer_secret
    
    if business_keys.paybill_number:
        shortcode = business_keys.paybill_number
        transaction_type = "CustomerPayBillOnline"
    elif business_keys.till_number:
        shortcode = business_keys.till_number
        transaction_type = "CustomerBuyGoodsOnline"
    else:
        # No shortcode configured
        return None

    passkey = current_app.config['MPESA_PASSKEY'] # Passkey might still be global for sandbox

    access_token = get_mpesa_access_token(consumer_key, consumer_secret)
    if not access_token:
        return None

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": transaction_type,
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
        "AccountReference": "CompanyXLTD",
        "TransactionDesc": "Payment of X"
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        # Log error response for debugging
        print(f"M-Pesa API Error: {response.text}")
        return None
