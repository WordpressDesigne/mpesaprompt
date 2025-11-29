from flask import render_template, redirect, url_for, flash, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.admin import admin
from app.models import User, Business, Transaction, Customer, Wallet
from app.admin.forms import (EditUserForm, EditBusinessForm, 
                            SearchForm, UserRegistrationForm, BusinessRegistrationForm)
from datetime import datetime, timedelta
import os
from functools import wraps

def admin_required(f):
    """Decorator to ensure the user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin.before_request
@login_required
@admin_required
def before_request():
    """Ensure the user is an admin for all admin routes."""
    pass

@admin.route('/')
@admin_required
def index():
    """Admin dashboard."""
    # Get statistics
    total_businesses = Business.query.count()
    total_users = User.query.count()
    total_transactions = Transaction.query.count()
    
    # Calculate total platform earnings (sum of all commissions)
    total_earnings = db.session.query(db.func.sum(Transaction.commission_amount))\
        .filter(Transaction.status == 'completed')\
        .scalar() or 0
    
    # Get recent transactions
    recent_transactions = Transaction.query\
        .order_by(Transaction.created_at.desc())\
        .limit(10).all()
    
    # Get recent signups
    recent_users = User.query\
        .order_by(User.created_at.desc())\
        .limit(5).all()
    
    return render_template('admin/index.html',
                         title='Admin Dashboard',
                         total_businesses=total_businesses,
                         total_users=total_users,
                         total_transactions=total_transactions,
                         total_earnings=total_earnings,
                         recent_transactions=recent_transactions,
                         recent_users=recent_users)

@admin.route('/users')
@admin_required
def users():
    """List all users."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    search = request.args.get('search')
    status = request.args.get('status', 'all')
    
    # Build query
    query = User.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) |
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term)) |
            (User.phone_number.ilike(search_term))
        )
    
    if status != 'all':
        query = query.filter(User.is_active == (status == 'active'))
    
    # Order and paginate
    pagination = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html',
                         title='Manage Users',
                         users=pagination.items,
                         pagination=pagination,
                         search=search,
                         status=status)

@admin.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View and edit user details."""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', title='User Details', user=user)

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        # Update user details
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        user.is_active = form.is_active.data
        user.is_admin = form.is_admin.data
        
        # Update password if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/edit_user.html', 
                         title='Edit User', 
                         form=form, 
                         user=user)

@admin.route('/users/new', methods=['GET', 'POST'])
@admin_required
def new_user():
    """Create a new user."""
    form = UserRegistrationForm()
    
    if form.validate_on_submit():
        # Create user
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            is_active=form.is_active.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.email} created successfully!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    return render_template('admin/new_user.html', 
                         title='Create New User', 
                         form=form)

@admin.route('/businesses')
@admin_required
def businesses():
    """List all businesses."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    search = request.args.get('search')
    status = request.args.get('status', 'all')
    
    # Build query
    query = Business.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Business.name.ilike(search_term)) |
            (Business.phone_number.ilike(search_term)) |
            (Business.mpesa_business_shortcode.ilike(search_term))
        )
    
    if status != 'all':
        query = query.filter(Business.is_active == (status == 'active'))
    
    # Order and paginate
    pagination = query.order_by(Business.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/businesses.html',
                         title='Manage Businesses',
                         businesses=pagination.items,
                         pagination=pagination,
                         search=search,
                         status=status)

@admin.route('/businesses/<int:business_id>')
@admin_required
def business_detail(business_id):
    """View business details."""
    business = Business.query.get_or_404(business_id)
    
    # Get business statistics
    total_transactions = Transaction.query.filter_by(business_id=business.id).count()
    total_customers = Customer.query.filter_by(business_id=business.id).count()
    
    # Calculate total amount processed
    total_amount = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.business_id == business.id)\
        .filter(Transaction.status == 'completed').scalar() or 0
    
    # Get recent transactions
    recent_transactions = Transaction.query\
        .filter_by(business_id=business.id)\
        .order_by(Transaction.created_at.desc())\
        .limit(5).all()
    
    return render_template('admin/business_detail.html',
                         title='Business Details',
                         business=business,
                         total_transactions=total_transactions,
                         total_customers=total_customers,
                         total_amount=total_amount,
                         recent_transactions=recent_transactions)

@admin.route('/businesses/<int:business_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_business(business_id):
    """Edit business details."""
    business = Business.query.get_or_404(business_id)
    form = EditBusinessForm(obj=business)
    
    if form.validate_on_submit():
        # Update business details
        form.populate_obj(business)
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file.filename != '':
                # In a real app, you'd want to process and save the file securely
                filename = f"business_{business.id}_{file.filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                business.logo = filename
        
        db.session.commit()
        flash('Business updated successfully!', 'success')
        return redirect(url_for('admin.business_detail', business_id=business.id))
    
    return render_template('admin/edit_business.html', 
                         title='Edit Business', 
                         form=form, 
                         business=business)

@admin.route('/businesses/new', methods=['GET', 'POST'])
@admin_required
def new_business():
    """Create a new business."""
    form = BusinessRegistrationForm()
    
    if form.validate_on_submit():
        # Create business
        business = Business(
            name=form.name.data,
            description=form.description.data,
            phone_number=form.phone_number.data,
            address=form.address.data,
            city=form.city.data,
            country=form.country.data,
            mpesa_consumer_key=form.mpesa_consumer_key.data,
            mpesa_consumer_secret=form.mpesa_consumer_secret.data,
            mpesa_business_shortcode=form.mpesa_business_shortcode.data,
            mpesa_passkey=form.mpesa_passkey.data,
            mpesa_callback_url=form.mpesa_callback_url.data,
            mpesa_environment=form.mpesa_environment.data,
            is_active=form.is_active.data
        )
        
        # Create wallet for business
        wallet = Wallet(balance=0.0, is_active=True)
        
        # Add to database
        db.session.add(business)
        db.session.flush()  # Get the business ID
        
        wallet.business_id = business.id
        db.session.add(wallet)
        
        # Add owner if user ID is provided
        owner_id = form.owner_id.data
        if owner_id:
            user = User.query.get(owner_id)
            if user:
                business.users.append(user)
        
        db.session.commit()
        
        flash(f'Business {business.name} created successfully!', 'success')
        return redirect(url_for('admin.business_detail', business_id=business.id))
    
    return render_template('admin/new_business.html', 
                         title='Create New Business', 
                         form=form)

@admin.route('/transactions')
@admin_required
def transactions():
    """List all transactions."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    search = request.args.get('search')
    status = request.args.get('status', 'all')
    business_id = request.args.get('business_id', type=int)
    
    # Build query
    query = Transaction.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Transaction.transaction_id.ilike(search_term)) |
            (Transaction.phone_number.ilike(search_term)) |
            (Transaction.account_reference.ilike(search_term)) |
            (Transaction.mpesa_receipt_number.ilike(search_term))
        )
    
    if status != 'all':
        query = query.filter(Transaction.status == status)
    
    if business_id:
        query = query.filter(Transaction.business_id == business_id)
    
    # Order and paginate
    pagination = query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Get businesses for filter dropdown
    businesses = Business.query.order_by(Business.name).all()
    
    return render_template('admin/transactions.html',
                         title='Manage Transactions',
                         transactions=pagination.items,
                         pagination=pagination,
                         search=search,
                         status=status,
                         business_id=business_id,
                         businesses=businesses)

@admin.route('/transactions/<int:transaction_id>')
@admin_required
def transaction_detail(transaction_id):
    """View transaction details."""
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('admin/transaction_detail.html', 
                         title='Transaction Details', 
                         transaction=transaction)

@admin.route('/customers')
@admin_required
def customers():
    """List all customers."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    search = request.args.get('search')
    business_id = request.args.get('business_id', type=int)
    
    # Build query
    query = Customer.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_term)) |
            (Customer.phone_number.ilike(search_term)) |
            (Customer.email.ilike(search_term))
        )
    
    if business_id:
        query = query.filter(Customer.business_id == business_id)
    
    # Order and paginate
    pagination = query.order_by(Customer.last_transaction.desc() if Customer.last_transaction else Customer.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Get businesses for filter dropdown
    businesses = Business.query.order_by(Business.name).all()
    
    return render_template('admin/customers.html',
                         title='Manage Customers',
                         customers=pagination.items,
                         pagination=pagination,
                         search=search,
                         business_id=business_id,
                         businesses=businesses)

@admin.route('/customers/<int:customer_id>')
@admin_required
def customer_detail(customer_id):
    """View customer details and transaction history."""
    customer = Customer.query.get_or_404(customer_id)
    
    # Get customer's transactions
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    transactions = Transaction.query.filter_by(customer_id=customer.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/customer_detail.html',
                         title='Customer Details',
                         customer=customer,
                         transactions=transactions)

@admin.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """Admin settings."""
    if request.method == 'POST':
        # Update settings
        current_app.config.update(
            SITE_NAME=request.form.get('site_name', current_app.config['SITE_NAME']),
            ITEMS_PER_PAGE=int(request.form.get('items_per_page', current_app.config['ITEMS_PER_PAGE'])),
            MAIL_SERVER=request.form.get('mail_server', current_app.config['MAIL_SERVER']),
            MAIL_PORT=int(request.form.get('mail_port', current_app.config['MAIL_PORT'])),
            MAIL_USE_TLS=request.form.get('mail_use_tls') == 'true',
            MAIL_USERNAME=request.form.get('mail_username', current_app.config['MAIL_USERNAME']),
            MAIL_DEFAULT_SENDER=request.form.get('mail_default_sender', current_app.config['MAIL_DEFAULT_SENDER']),
            UPLOAD_FOLDER=request.form.get('upload_folder', current_app.config['UPLOAD_FOLDER']),
            MAX_CONTENT_LENGTH=int(request.form.get('max_content_length', current_app.config['MAX_CONTENT_LENGTH'])),
            COMMISSION_RATE=float(request.form.get('commission_rate', current_app.config['COMMISSION_RATE']))
        )
        
        # Save to config file or database in a real app
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', title='Admin Settings')

@admin.route('/logs')
@admin_required
def logs():
    """View application logs."""
    # In a real app, you would read from a log file or database
    # For now, we'll just show a placeholder
    return render_template('admin/logs.html', title='Application Logs')

@admin.route('/api/export/transactions')
@admin_required
def export_transactions():
    """Export transactions to CSV."""
    import csv
    from io import StringIO
    
    # Get filter parameters
    status = request.args.get('status')
    business_id = request.args.get('business_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = Transaction.query
    
    if status and status != 'all':
        query = query.filter(Transaction.status == status)
    
    if business_id:
        query = query.filter(Transaction.business_id == business_id)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Transaction.created_at >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Transaction.created_at <= end_date)
        except ValueError:
            pass
    
    # Execute query
    transactions = query.order_by(Transaction.created_at.desc()).all()
    
    # Create CSV in memory
    si = StringIO()
    cw = csv.writer(si)
    
    # Write header
    cw.writerow([
        'Transaction ID',
        'Date',
        'Business',
        'Customer',
        'Phone Number',
        'Amount',
        'Status',
        'M-Pesa Receipt',
        'Reference',
        'Description',
        'Commission'
    ])
    
    # Write data
    for t in transactions:
        cw.writerow([
            t.transaction_id or '',
            t.created_at.strftime('%Y-%m-%d %H:%M:%S') if t.created_at else '',
            t.business.name if t.business else '',
            t.customer.name if t.customer else '',
            t.phone_number or '',
            str(t.amount) if t.amount is not None else '0.00',
            t.status or '',
            t.mpesa_receipt_number or '',
            t.account_reference or '',
            t.transaction_desc or '',
            str(t.commission_amount) if t.commission_amount is not None else '0.00'
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    # Create response
    from flask import make_response
    response = make_response(output)
    response.headers['Content-Disposition'] = 'attachment; filename=transactions_export.csv'
    response.headers['Content-type'] = 'text/csv'
    return response
