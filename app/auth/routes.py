from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import auth
from app.auth.forms import (LoginForm, RegistrationForm, 
                           MpesaCredentialsForm, ResetPasswordRequestForm, ResetPasswordForm)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create user
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            is_active=True
        )
        user.set_password(form.password.data)
        
        # Create business
        business = Business(
            name=form.business_name.data,
            phone_number=form.business_phone.data,
            address=form.address.data,
            city=form.city.data,
            country=form.country.data,
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
                         form=form)

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
