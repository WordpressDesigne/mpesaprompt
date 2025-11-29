from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import auth
from app.auth.forms import (LoginForm, RegistrationForm, BusinessRegistrationForm, 
                           MpesaCredentialsForm, ResetPasswordRequestForm, ResetPasswordForm)
from app.models import User, Business, Wallet
from app.auth.email import send_password_reset_email
from datetime import datetime

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash('You have been logged in successfully!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user_form = RegistrationForm()
    business_form = BusinessRegistrationForm()
    
    if user_form.validate_on_submit() and business_form.validate_on_submit():
        # Create user
        user = User(
            first_name=user_form.first_name.data,
            last_name=user_form.last_name.data,
            email=user_form.email.data,
            phone_number=user_form.phone_number.data,
            is_active=True
        )
        user.set_password(user_form.password.data)
        
        # Create business
        business = Business(
            name=business_form.business_name.data,
            phone_number=business_form.business_phone.data,
            address=business_form.address.data,
            city=business_form.city.data,
            country=business_form.country.data,
            is_active=True
        )
        
        # Create wallet for business
        wallet = Wallet(balance=0.0, is_active=True)
        
        # Add relationships
        db.session.add(user)
        db.session.add(business)
        db.session.flush()  # Get the IDs
        
        wallet.business_id = business.id
        db.session.add(wallet)
        
        # Add user to business
        business.users.append(user)
        
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        login_user(user)
        
        return redirect(url_for('auth.setup_mpesa'))
    
    return render_template('auth/register.html', 
                         title='Register',
                         user_form=user_form,
                         business_form=business_form)

@auth.route('/setup-mpesa', methods=['GET', 'POST'])
@login_required
def setup_mpesa():
    """Setup M-Pesa credentials for the business."""
    # Get the user's business
    if not current_user.businesses:
        flash('You need to create a business first.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    business = current_user.businesses[0]  # Assuming one business per user for now
    form = MpesaCredentialsForm()
    
    if form.validate_on_submit():
        # Update business with M-Pesa credentials
        business.mpesa_consumer_key = form.consumer_key.data
        business.mpesa_consumer_secret = form.consumer_secret.data
        business.mpesa_business_shortcode = form.business_shortcode.data
        business.mpesa_passkey = form.passkey.data
        business.mpesa_callback_url = form.callback_url.data
        business.mpesa_environment = form.environment.data
        
        # Test M-Pesa connection (simplified for now)
        try:
            # In a real app, you would test the M-Pesa API connection here
            # For now, we'll just save the credentials
            db.session.commit()
            flash('M-Pesa credentials saved successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error saving M-Pesa credentials: {str(e)}')
            flash('Failed to save M-Pesa credentials. Please try again.', 'danger')
    
    # Pre-fill with sandbox values for testing
    if not form.is_submitted():
        form.consumer_key.data = business.mpesa_consumer_key or ''
        form.consumer_secret.data = business.mpesa_consumer_secret or ''
        form.business_shortcode.data = business.mpesa_business_shortcode or ''
        form.passkey.data = business.mpesa_passkey or ''
        form.callback_url.data = business.mpesa_callback_url or url_for('api.mpesa_callback', _external=True)
        form.environment.data = business.mpesa_environment or 'sandbox'
    
    return render_template('auth/setup_mpesa.html', 
                         title='Setup M-Pesa',
                         form=form)

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html',
                         title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
