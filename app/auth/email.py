from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread
import jwt
from datetime import datetime, timedelta

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    """Send a password reset email to the user."""
    token = user.get_reset_password_token()
    send_email(
        'Reset Your Password',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

def send_welcome_email(user):
    """Send a welcome email to the new user."""
    send_email(
        'Welcome to M-Pesa STK Push SaaS',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template('email/welcome.txt', user=user),
        html_body=render_template('email/welcome.html', user=user)
    )

def send_mpesa_credentials_updated(user):
    """Send notification when M-Pesa credentials are updated."""
    send_email(
        'M-Pesa Credentials Updated',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template('email/mpesa_credentials_updated.txt', user=user),
        html_body=render_template('email/mpesa_credentials_updated.html', user=user)
    )

def send_transaction_receipt(transaction, user_email):
    """Send a transaction receipt to the user."""
    send_email(
        f'Payment Receipt - {transaction.transaction_id}',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user_email],
        text_body=render_template('email/transaction_receipt.txt', transaction=transaction),
        html_body=render_template('email/transaction_receipt.html', transaction=transaction)
    )
