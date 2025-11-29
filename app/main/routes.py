from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.main import main
from app.models import User, Business, Transaction, Customer, Wallet
from datetime import datetime, timedelta
import json

@main.route('/')
def index():
    """Home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]  # Assuming one business per user for now
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(business_id=business.id)\
        .order_by(Transaction.created_at.desc())\
        .limit(5).all()
    
    # Get recent customers
    recent_customers = Customer.query.filter_by(business_id=business.id)\
        .order_by(Customer.last_transaction.desc() if Customer.last_transaction else Customer.created_at.desc())\
        .limit(5).all()
    
    # Calculate stats
    total_transactions = Transaction.query.filter_by(business_id=business.id).count()
    total_customers = Customer.query.filter_by(business_id=business.id).count()
    
    # Calculate total amount processed
    total_amount = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.business_id == business.id)\
        .filter(Transaction.status == 'completed').scalar() or 0
    
    # Calculate today's transactions
    today = datetime.utcnow().date()
    today_transactions = Transaction.query\
        .filter(Transaction.business_id == business.id)\
        .filter(db.func.date(Transaction.created_at) == today)\
        .count()
    
    # Get transaction data for the last 7 days for the chart
    date_7_days_ago = datetime.utcnow() - timedelta(days=6)  # 6 days + today = 7 days
    
    # Get daily transaction counts
    daily_transactions = db.session.query(
        db.func.date(Transaction.created_at).label('date'),
        db.func.count(Transaction.id).label('count')
    ).filter(
        Transaction.business_id == business.id,
        Transaction.created_at >= date_7_days_ago
    ).group_by(
        db.func.date(Transaction.created_at)
    ).order_by(
        db.func.date(Transaction.created_at)
    ).all()
    
    # Format data for chart
    dates = []
    counts = []
    
    # Initialize with 0 for all 7 days
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6-i)).date()
        dates.append(date.strftime('%a'))  # Day name (Mon, Tue, etc.)
        counts.append(0)  # Default to 0
    
    # Update with actual data
    for dt in daily_transactions:
        day_index = (datetime.utcnow().date() - dt.date).days
        if 0 <= day_index < 7:  # Ensure it's within the last 7 days
            counts[6 - day_index] = dt.count
    
    return render_template('main/dashboard.html',
                         title='Dashboard',
                         recent_transactions=recent_transactions,
                         recent_customers=recent_customers,
                         total_transactions=total_transactions,
                         total_customers=total_customers,
                         total_amount=total_amount,
                         today_transactions=today_transactions,
                         chart_dates=json.dumps(dates),
                         chart_counts=json.dumps(counts))

@main.route('/transactions')
@login_required
def transactions():
    """View all transactions."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    status = request.args.get('status')
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
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
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Transaction.created_at >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Include the entire end date
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Transaction.created_at <= end_date)
        except ValueError:
            pass
    
    # Order and paginate
    transactions = query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/transactions.html',
                         title='Transactions',
                         transactions=transactions,
                         status=status,
                         search=search,
                         start_date=start_date,
                         end_date=end_date)

@main.route('/customers')
@login_required
def customers():
    """View all customers."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search = request.args.get('search')
    
    # Build query
    query = Customer.query.filter_by(business_id=business.id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_term)) |
            (Customer.phone_number.ilike(search_term)) |
            (Customer.email.ilike(search_term))
        )
    
    # Order and paginate
    customers = query.order_by(Customer.last_transaction.desc() if Customer.last_transaction else Customer.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/customers.html',
                         title='Customers',
                         customers=customers,
                         search=search)

@main.route('/wallet')
@login_required
def wallet():
    """View wallet and transaction history."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    wallet = business.wallet
    
    # Get transaction history
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    transactions = Transaction.query\
        .filter_by(business_id=business.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/wallet.html',
                         title='My Wallet',
                         wallet=wallet,
                         transactions=transactions)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User and business settings."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    
    # Handle form submission
    if request.method == 'POST':
        # Update user details
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        current_user.phone_number = request.form.get('phone_number', current_user.phone_number)
        
        # Update business details
        business.name = request.form.get('business_name', business.name)
        business.phone_number = request.form.get('business_phone', business.phone_number)
        business.address = request.form.get('business_address', business.address)
        business.city = request.form.get('business_city', business.city)
        business.country = request.form.get('business_country', business.country)
        
        # Handle logo upload
        if 'business_logo' in request.files:
            file = request.files['business_logo']
            if file.filename != '':
                # In a real app, you'd want to process and save the file securely
                filename = f"business_{business.id}_{file.filename}"
                file.save(f"app/static/uploads/{filename}")
                business.logo = f"uploads/{filename}"
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('main/settings.html',
                         title='Settings',
                         business=business)

@main.route('/send-money', methods=['GET', 'POST'])
@login_required
def send_money():
    """Send money via M-Pesa STK push."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    wallet = business.wallet
    
    if request.method == 'POST':
        phone = request.form.get('phone')
        amount = float(request.form.get('amount', 0))
        reference = request.form.get('reference', '')
        description = request.form.get('description', '')
        
        # Basic validation
        if not phone or not amount or amount <= 0:
            flash('Please provide valid phone number and amount', 'danger')
            return redirect(url_for('main.send_money'))
        
        # Format phone number (add country code if not present)
        if not phone.startswith('254'):
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif phone.startswith('+254'):
                phone = phone[1:]
            else:
                phone = '254' + phone
        
        # In a real app, you would call the M-Pesa API here
        # For now, we'll simulate a successful transaction
        from datetime import datetime
        import random
        import string
        
        # Generate a random transaction ID
        transaction_id = 'MP' + ''.join(random.choices(string.digits, k=8))
        
        # Create a new transaction record
        transaction = Transaction(
            transaction_id=transaction_id,
            amount=amount,
            phone_number=phone,
            account_reference=reference,
            transaction_desc=description or f"Payment to {phone}",
            status='pending',
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
        
        # Add to database
        db.session.add(transaction)
        
        # Simulate M-Pesa callback after a short delay
        from threading import Timer
        
        def update_transaction_status():
            with current_app.app_context():
                from app import create_app
                app = create_app()
                with app.app_context():
                    transaction = Transaction.query.get(transaction.id)
                    if transaction:
                        # 90% success rate for simulation
                        import random
                        if random.random() < 0.9:
                            transaction.status = 'completed'
                            transaction.result_code = '0'
                            transaction.result_desc = 'The service request is processed successfully.'
                            transaction.mpesa_receipt_number = 'NCB' + ''.join(random.choices(string.digits, k=7))
                            transaction.transaction_date = datetime.utcnow()
                            
                            # Update wallet
                            wallet.balance += amount
                            wallet.total_earnings += amount
                            
                            # Calculate and deduct commission
                            commission = amount * 0.01  # 1% commission
                            wallet.total_commissions += commission
                            wallet.balance -= commission
                            
                            transaction.commission_amount = commission
                        else:
                            transaction.status = 'failed'
                            transaction.result_code = '1'
                            transaction.result_desc = 'The balance is insufficient for the transaction.'
                        
                        transaction.updated_at = datetime.utcnow()
                        db.session.commit()
        
        # Schedule the callback after 5 seconds
        Timer(5.0, update_transaction_status).start()
        
        db.session.commit()
        
        flash('Payment request sent successfully!', 'success')
        return redirect(url_for('main.transaction_details', transaction_id=transaction.id))
    
    return render_template('main/send_money.html',
                         title='Send Money',
                         wallet=wallet)

@main.route('/transaction/<transaction_id>')
@login_required
def transaction_details(transaction_id):
    """View transaction details."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        business_id=business.id
    ).first_or_404()
    
    return render_template('main/transaction_details.html',
                         title='Transaction Details',
                         transaction=transaction)

@main.route('/customer/<int:customer_id>')
@login_required
def customer_details(customer_id):
    """View customer details and transaction history."""
    if not current_user.businesses:
        return redirect(url_for('auth.setup_business'))
    
    business = current_user.businesses[0]
    
    customer = Customer.query.filter_by(
        id=customer_id,
        business_id=business.id
    ).first_or_404()
    
    # Get customer's transactions
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    transactions = Transaction.query.filter_by(
        customer_id=customer.id,
        business_id=business.id
    ).order_by(
        Transaction.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/customer_details.html',
                         title='Customer Details',
                         customer=customer,
                         transactions=transactions)
