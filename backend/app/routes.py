from flask import Blueprint, request, jsonify, send_file, abort
from app import db, jwt
from app.models import Business, APIKeys, Transaction, Customer, Wallet, CommissionLedger, AdminUser
from app.services import stk_push
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
import datetime
import openpyxl
from io import BytesIO
from functools import wraps

bp = Blueprint('main', __name__)

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            if claims['role'] != 'admin':
                abort(403)
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@bp.route('/health')
def health_check():
    return {'status': 'ok'}

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not 'name' in data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    if Business.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Business with this email already exists'}), 400

    new_business = Business(name=data['name'], email=data['email'])
    new_business.set_password(data['password'])
    db.session.add(new_business)
    db.session.commit()

    # Create a wallet for the new business
    new_wallet = Wallet(business_id=new_business.id)
    db.session.add(new_wallet)
    db.session.commit()

    return jsonify({'message': 'Business created successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    business = Business.query.filter_by(email=data['email']).first()
    if not business or not business.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'id': business.id, 'role': 'business'})
    return jsonify(access_token=access_token), 200

@bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    admin = AdminUser.query.filter_by(email=data['email']).first()
    if not admin or not admin.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'id': admin.id, 'role': 'admin'})
    return jsonify(access_token=access_token), 200

@bp.route('/dashboard')
@jwt_required()
def dashboard():
    current_identity = get_jwt_identity()
    if current_identity['role'] == 'business':
        business = Business.query.get(current_identity['id'])
        return jsonify({'name': business.name, 'role': 'business'}), 200
    elif current_identity['role'] == 'admin':
        admin = AdminUser.query.get(current_identity['id'])
        return jsonify({'email': admin.email, 'role': 'admin'}), 200
    return jsonify({'message': 'Invalid role'}), 403

@bp.route('/settings/update', methods=['POST'])
@jwt_required()
def update_settings():
    current_business_id = get_jwt_identity()['id']
    business = Business.query.get(current_business_id)
    data = request.get_json()

    if not data or not 'consumer_key' in data or not 'consumer_secret' in data:
        return jsonify({'message': 'Missing consumer key or secret'}), 400

    if 'till_number' not in data and 'paybill_number' not in data:
        return jsonify({'message': 'Missing till number or paybill number'}), 400

    api_keys = business.api_keys
    if not api_keys:
        api_keys = APIKeys(business_id=current_business_id)

    api_keys.consumer_key = data['consumer_key']
    api_keys.consumer_secret = data['consumer_secret']
    api_keys.till_number = data.get('till_number')
    api_keys.paybill_number = data.get('paybill_number')

    db.session.add(api_keys)
    db.session.commit()

    # Perform automated test STK push
    test_phone_number = "254708374149" # A test phone number from Safaricom documentation
    test_amount = 1
    stk_push_result = stk_push(test_phone_number, test_amount)

    if stk_push_result and stk_push_result.get("ResponseCode") == "0":
        return jsonify({'message': 'Settings updated and test STK push successful'}), 200
    else:
        # For simplicity, we are not rolling back the settings update.
        # In a real application, you might want to handle this differently.
        return jsonify({'message': 'Settings updated, but test STK push failed'}), 200

@bp.route('/settings')
@jwt_required()
def get_settings():
    current_business_id = get_jwt_identity()['id']
    business = Business.query.get(current_business_id)
    
    api_keys = business.api_keys
    if api_keys:
        return jsonify({
            'consumer_key': api_keys.consumer_key,
            'consumer_secret': api_keys.consumer_secret,
            'till_number': api_keys.till_number,
            'paybill_number': api_keys.paybill_number
        }), 200
    else:
        return jsonify({'message': 'API keys not set'}), 404

@bp.route('/stk-push', methods=['POST'])
@jwt_required()
def send_stk_push():
    current_business_id = get_jwt_identity()['id']
    data = request.get_json()

    if not data or not 'phone_number' in data or not 'amount' in data:
        return jsonify({'message': 'Missing phone number or amount'}), 400

    phone_number = data['phone_number']
    amount = data['amount']

    stk_push_result = stk_push(phone_number, amount)

    if stk_push_result and stk_push_result.get("ResponseCode") == "0":
        # Log the transaction
        new_transaction = Transaction(
            amount=amount,
            phone_number=phone_number,
            checkout_request_id=stk_push_result['CheckoutRequestID'],
            business_id=current_business_id
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'STK push sent successfully'}), 200
    else:
        return jsonify({'message': 'STK push failed'}), 400

@bp.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()

    if data and data.get('Body') and data['Body'].get('stkCallback'):
        stk_callback = data['Body']['stkCallback']
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')

        transaction = Transaction.query.filter_by(checkout_request_id=checkout_request_id).first()

        if transaction:
            if result_code == 0:
                transaction.status = 'success'
                
                # Update or create customer
                customer = Customer.query.filter_by(phone_number=transaction.phone_number, business_id=transaction.business_id).first()
                if not customer:
                    customer = Customer(
                        phone_number=transaction.phone_number,
                        business_id=transaction.business_id
                    )
                    db.session.add(customer)
                
                customer.total_amount_requested += transaction.amount
                customer.transaction_count += 1
                customer.last_transaction_date = datetime.datetime.utcnow()
                transaction.customer_id = customer.id

                # Commission logic
                business = Business.query.get(transaction.business_id)
                commission_amount = transaction.amount * 0.01
                business.wallet.balance -= commission_amount

                new_commission_entry = CommissionLedger(
                    amount=commission_amount,
                    wallet_id=business.wallet.id
                )
                db.session.add(new_commission_entry)

            else:
                transaction.status = 'failed'
            
            db.session.commit()

    return jsonify({'message': 'Callback received'}), 200

@bp.route('/customers')
@jwt_required()
def get_customers():
    current_business_id = get_jwt_identity()['id']
    customers = Customer.query.filter_by(business_id=current_business_id).all()
    
    customer_list = []
    for customer in customers:
        customer_list.append({
            'name': customer.name,
            'phone_number': customer.phone_number,
            'total_amount_requested': customer.total_amount_requested,
            'transaction_count': customer.transaction_count,
            'first_transaction_date': customer.first_transaction_date.strftime('%Y-%m-%d %H:%M:%S') if customer.first_transaction_date else None,
            'last_transaction_date': customer.last_transaction_date.strftime('%Y-%m-%d %H:%M:%S') if customer.last_transaction_date else None
        })

    return jsonify(customer_list), 200

@bp.route('/customers/export-excel')
@jwt_required()
def export_customers_excel():
    current_business_id = get_jwt_identity()['id']
    customers = Customer.query.filter_by(business_id=current_business_id).all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Customers"

    # Add headers
    headers = ["Name", "Phone Number", "Total Amount Requested", "Transaction Count", "First Transaction Date", "Last Transaction Date"]
    sheet.append(headers)

    # Add data
    for customer in customers:
        sheet.append([
            customer.name,
            customer.phone_number,
            customer.total_amount_requested,
            customer.transaction_count,
            customer.first_transaction_date.strftime('%Y-%m-%d %H:%M:%S') if customer.first_transaction_date else None,
            customer.last_transaction_date.strftime('%Y-%m-%d %H:%M:%S') if customer.last_transaction_date else None
        ])

    # Save the workbook to a BytesIO object
    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    return send_file(
        excel_file,
        as_attachment=True,
        download_name="customers.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@bp.route('/wallet')
@jwt_required()
def get_wallet_info():
    current_business_id = get_jwt_identity()['id']
    business = Business.query.get(current_business_id)
    
    wallet_info = {
        'balance': business.wallet.balance,
        'commission_ledgers': []
    }

    for ledger_entry in business.wallet.commission_ledgers:
        wallet_info['commission_ledgers'].append({
            'amount': ledger_entry.amount,
            'timestamp': ledger_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(wallet_info), 200

@bp.route('/admin/businesses')
@jwt_required()
@admin_required()
def get_all_businesses():
    businesses = Business.query.all()
    
    business_list = []
    for business in businesses:
        business_list.append({
            'id': business.id,
            'name': business.name,
            'email': business.email,
            'created_at': business.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': business.is_active
        })

    return jsonify(business_list), 200

@bp.route('/admin/suspend/<int:business_id>', methods=['POST'])
@jwt_required()
@admin_required()
def suspend_business(business_id):
    business = Business.query.get(business_id)
    if not business:
        return jsonify({'message': 'Business not found'}), 404
    business.is_active = False
    db.session.commit()
    return jsonify({'message': 'Business suspended successfully'}), 200

@bp.route('/admin/reactivate/<int:business_id>', methods=['POST'])
@jwt_required()
@admin_required()
def reactivate_business(business_id):
    business = Business.query.get(business_id)
    if not business:
        return jsonify({'message': 'Business not found'}), 404
    business.is_active = True
    db.session.commit()
    return jsonify({'message': 'Business reactivated successfully'}), 200

@bp.route('/admin/transactions')
@jwt_required()
@admin_required()
def get_all_transactions():
    transactions = Transaction.query.all()
    
    transaction_list = []
    for transaction in transactions:
        transaction_list.append({
            'id': transaction.id,
            'amount': transaction.amount,
            'phone_number': transaction.phone_number,
            'status': transaction.status,
            'checkout_request_id': transaction.checkout_request_id,
            'timestamp': transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'business_id': transaction.business_id,
            'customer_id': transaction.customer_id
        })

    return jsonify(transaction_list), 200

@bp.route('/admin/commissions')
@jwt_required()
@admin_required()
def get_all_commissions():
    commission_ledgers = CommissionLedger.query.all()
    
    commission_list = []
    for ledger_entry in commission_ledgers:
        commission_list.append({
            'id': ledger_entry.id,
            'amount': ledger_entry.amount,
            'timestamp': ledger_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'business_id': ledger_entry.wallet.business_id
        })

    return jsonify(commission_list), 200

@bp.route('/admin/set-commission', methods=['POST'])
@jwt_required()
@admin_required()
def set_commission():
    data = request.get_json()
    if not data or 'commission_rate' not in data:
        return jsonify({'message': 'Missing commission_rate'}), 400
    
    new_commission_rate = data['commission_rate']
    # For now, just print the new commission rate.
    # In a real application, you would store this in the database or a configuration.
    print(f"New commission rate set to: {new_commission_rate}%")

    return jsonify({'message': f'Commission rate set to {new_commission_rate}% successfully'}), 200

@bp.route('/admin/impersonate/<int:business_id>', methods=['GET'])
@jwt_required()
@admin_required()
def impersonate_business(business_id):
    business = Business.query.get(business_id)
    if not business:
        return jsonify({'message': 'Business not found'}), 404
    
    access_token = create_access_token(identity={'id': business.id, 'role': 'business'})
    return jsonify(access_token=access_token), 200

@bp.route('/admin/customers/export-excel')
@jwt_required()
@admin_required()
def export_all_customers_excel():
    customers = Customer.query.all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "All Customers"

    # Add headers
    headers = ["Business ID", "Name", "Phone Number", "Total Amount Requested", "Transaction Count", "First Transaction Date", "Last Transaction Date"]
    sheet.append(headers)

    # Add data
    for customer in customers:
        sheet.append([
            customer.business_id,
            customer.name,
            customer.phone_number,
            customer.total_amount_requested,
            customer.transaction_count,
            customer.first_transaction_date.strftime('%Y-%m-%d %H:%M:%S') if customer.first_transaction_date else None,
            customer.last_transaction_date.strftime('%Y-%m-%d %H:%M:%S') if customer.last_transaction_date else None
        ])

    # Save the workbook to a BytesIO object
    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)

    return send_file(
        excel_file,
        as_attachment=True,
        download_name="all_customers.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )