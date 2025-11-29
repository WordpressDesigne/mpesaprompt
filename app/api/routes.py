from flask import jsonify, request, current_app, url_for
from flask_login import current_user, login_required
from app import db
from app.api import api
from app.models import Business, Transaction, Customer, Wallet
from datetime import datetime
import base64
import requests
import json
import hashlib
import time
import os

# Global token cache
_mpesa_token = None
_mpesa_token_expiry = 0

@api.route('/status')
def status():
    """API status endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

def get_mpesa_auth_token(business):
    """Get M-Pesa API authentication token."""
    global _mpesa_token, _mpesa_token_expiry
    
    # Check if we have a valid cached token
    if _mpesa_token and time.time() < _mpesa_token_expiry - 60:  # 1 minute buffer
        return _mpesa_token
    
    # Get the appropriate base URL based on environment
    if business.mpesa_environment == 'production':
        base_url = 'https://api.safaricom.co.ke'
    else:
        base_url = 'https://sandbox.safaricom.co.ke'
    
    # Generate auth string
    auth_string = f"{business.mpesa_consumer_key}:{business.mpesa_consumer_secret}"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    # Request token
    url = f"{base_url}/oauth/v1/generate?grant_type=client_credentials"
    headers = {
        'Authorization': f'Basic {base64_auth}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Cache the token
        _mpesa_token = data['access_token']
        _mpesa_token_expiry = time.time() + int(data.get('expires_in', 3599))
        
        current_app.logger.info('Successfully obtained M-Pesa access token')
        return _mpesa_token
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Error obtaining M-Pesa token: {str(e)}')
        return None

def initiate_stk_push(business, phone, amount, account_reference, transaction_desc):
    """Initiate M-Pesa STK push to customer."""
    # Get the appropriate base URL based on environment
    if business.mpesa_environment == 'production':
        base_url = 'https://api.safaricom.co.ke'
    else:
        base_url = 'https://sandbox.safaricom.co.ke'
    
    # Get authentication token
    token = get_mpesa_auth_token(business)
    if not token:
        return None, 'Failed to obtain authentication token'
    
    # Format phone number (ensure it starts with 254)
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('+254'):
        phone = phone[1:]
    elif not phone.startswith('254'):
        phone = '254' + phone
    
    # Prepare request data
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{business.mpesa_business_shortcode}{business.mpesa_passkey}{timestamp}".encode()
    ).decode()
    
    payload = {
        'BusinessShortCode': business.mpesa_business_shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone,
        'PartyB': business.mpesa_business_shortcode,
        'PhoneNumber': phone,
        'CallBackURL': business.mpesa_callback_url or \
                      url_for('api.mpesa_callback', _external=True),
        'AccountReference': account_reference[:12],  # Max 12 characters
        'TransactionDesc': transaction_desc[:13]     # Max 13 characters
    }
    
    # Make the STK push request
    url = f"{base_url}/mpesa/stkpush/v1/processrequest"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response:
            try:
                error_msg = e.response.json().get('errorMessage', str(e))
            except:
                error_msg = e.response.text or str(e)
        return None, error_msg

@api.route('/mpesa/stk-push', methods=['POST'])
@login_required
def stk_push():
    """Initiate STK push to customer."""
    if not current_user.businesses:
        return jsonify({'error': 'No business account found'}), 400
    
    business = current_user.businesses[0]  # Assuming one business per user for now
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    phone = data.get('phone')
    amount = data.get('amount')
    account_reference = data.get('reference', 'Payment')
    transaction_desc = data.get('description', 'Payment')
    
    # Validate input
    if not phone or not amount:
        return jsonify({'error': 'Phone and amount are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount must be greater than 0')
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Create transaction record
    transaction = Transaction(
        amount=amount,
        phone_number=phone,
        account_reference=account_reference,
        transaction_desc=transaction_desc,
        status='initiated',
        business_id=business.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Find or create customer
    customer = Customer.query.filter_by(
        phone_number=phone,
        business_id=business.id
    ).first()
    
    if not customer:
        customer = Customer(
            name=f"Customer {phone}",
            phone_number=phone,
            business_id=business.id,
            first_transaction=datetime.utcnow(),
            last_transaction=datetime.utcnow(),
            total_transactions=1,
            total_amount=amount
        )
        db.session.add(customer)
    else:
        customer.total_transactions += 1
        customer.total_amount += amount
        customer.last_transaction = datetime.utcnow()
    
    # Set customer for transaction
    transaction.customer = customer
    db.session.add(transaction)
    db.session.commit()
    
    # Initiate STK push
    response, error = initiate_stk_push(
        business=business,
        phone=phone,
        amount=amount,
        account_reference=account_reference,
        transaction_desc=transaction_desc
    )
    
    if error:
        transaction.status = 'failed'
        transaction.result_desc = error
        db.session.commit()
        return jsonify({'error': error}), 400
    
    # Update transaction with response
    transaction.transaction_id = response.get('MerchantRequestID')
    transaction.status = 'pending'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'STK push initiated successfully',
        'transaction_id': transaction.id,
        'merchant_request_id': response.get('MerchantRequestID'),
        'checkout_request_id': response.get('CheckoutRequestID'),
        'response_code': response.get('ResponseCode'),
        'response_description': response.get('ResponseDescription')
    })

@api.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa callback with transaction status."""
    try:
        # Log the raw callback data for debugging
        callback_data = request.get_json(force=True)
        current_app.logger.info(f'M-Pesa Callback Received: {json.dumps(callback_data, indent=2)}')
        
        # Safely extract the nested data
        body = callback_data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        # Get the checkout request ID and result code
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        # Find the transaction by checkout request ID
        transaction = Transaction.query.filter_by(
            checkout_request_id=checkout_request_id
        ).first()
        
        if not transaction:
            current_app.logger.error(f'Transaction not found for CheckoutRequestID: {checkout_request_id}')
            return jsonify({'ResultCode': 0, 'ResultDesc': 'Transaction not found'}), 404
        
        # Update transaction status based on result code
        if result_code == '0':
            # Success - extract payment details
            metadata = {}
            for item in stk_callback.get('CallbackMetadata', {}).get('Item', []):
                if 'Name' in item and 'Value' in item:
                    metadata[item['Name']] = item['Value']
            
            transaction.status = 'completed'
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            transaction.mpesa_receipt_number = metadata.get('MpesaReceiptNumber')
            transaction.transaction_date = datetime.utcnow()
            transaction.amount = float(metadata.get('Amount', transaction.amount))
            transaction.phone_number = metadata.get('PhoneNumber', transaction.phone_number)
            
            # Update customer's total amount and last transaction
            customer = transaction.customer
            if customer:
                customer.total_amount = (customer.total_amount or 0) + transaction.amount
                customer.last_transaction = datetime.utcnow()
                
                # Update customer name if not set and we have it in metadata
                if not customer.name and 'FirstName' in metadata and 'MiddleName' in metadata and 'LastName' in metadata:
                    customer.name = f"{metadata['FirstName']} {metadata['MiddleName']} {metadata['LastName']}"
            
            # Update business wallet
            wallet = transaction.business.wallet
            if wallet:
                wallet.balance = (wallet.balance or 0) + transaction.amount
                wallet.total_earnings = (wallet.total_earnings or 0) + transaction.amount
                
                # Calculate and deduct commission (1%)
                commission = transaction.amount * 0.01
                wallet.total_commissions = (wallet.total_commissions or 0) + commission
                wallet.balance -= commission
                
                transaction.commission_amount = commission
            
            current_app.logger.info(f'Payment completed: {transaction.mpesa_receipt_number}')
        else:
            # Failed transaction
            transaction.status = 'failed'
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            current_app.logger.warning(f'Payment failed: {result_desc}')
        
        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Always return success to M-Pesa
        return jsonify({
            'ResultCode': 0,
            'ResultDesc': 'The service was accepted successfully',
            'ThirdPartyTransID': transaction.mpesa_receipt_number or ''
        })
    
    except Exception as e:
        current_app.logger.error(f'Error processing M-Pesa callback: {str(e)}', exc_info=True)
        # Still return success to M-Pesa to prevent retries for this error
        return jsonify({
            'ResultCode': 0,
            'ResultDesc': 'The service was accepted successfully',
            'error': str(e)
        }), 200

@api.route('/transactions')
@login_required
def get_transactions():
    """Get paginated list of transactions for the authenticated user's business."""
    if not current_user.businesses:
        return jsonify({'error': 'No business account found'}), 400
    
    business = current_user.businesses[0]  # Assuming one business per user for now
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Build query
    query = Transaction.query.filter_by(business_id=business.id)
    
    if status and status != 'all':
        query = query.filter(Transaction.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Transaction.phone_number.ilike(search_term)) |
            (Transaction.transaction_id.ilike(search_term)) |
            (Transaction.account_reference.ilike(search_term))
        )
    
    # Order and paginate
    pagination = query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Format response
    transactions = [{
        'id': t.id,
        'transaction_id': t.transaction_id,
        'amount': float(t.amount),
        'phone_number': t.phone_number,
        'status': t.status,
        'account_reference': t.account_reference,
        'transaction_desc': t.transaction_desc,
        'created_at': t.created_at.isoformat() if t.created_at else None,
        'updated_at': t.updated_at.isoformat() if t.updated_at else None,
        'mpesa_receipt_number': t.mpesa_receipt_number,
        'result_code': t.result_code,
        'result_desc': t.result_desc
    } for t in pagination.items]
    
    return jsonify({
        'transactions': transactions,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })

@api.route('/customers')
@login_required
def get_customers():
    """Get paginated list of customers for the authenticated user's business."""
    if not current_user.businesses:
        return jsonify({'error': 'No business account found'}), 400
    
    business = current_user.businesses[0]  # Assuming one business per user for now
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Customer.query.filter_by(business_id=business.id)
    
    # Order by last transaction or creation date
    query = query.order_by(
        Customer.last_transaction.desc() if Customer.last_transaction else Customer.created_at.desc()
    )
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format response
    customers = [{
        'id': c.id,
        'name': c.name,
        'phone_number': c.phone_number,
        'email': c.email,
        'total_transactions': c.total_transactions,
        'total_amount': float(c.total_amount) if c.total_amount else 0.0,
        'first_transaction': c.first_transaction.isoformat() if c.first_transaction else None,
        'last_transaction': c.last_transaction.isoformat() if c.last_transaction else None,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in pagination.items]
    
    return jsonify({
        'customers': customers,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })
