from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User, Business

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class BusinessRegistrationForm(FlaskForm):
    """Form for business registration during user signup."""
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=120)])
    business_type = SelectField('Business Type', choices=[
        ('individual', 'Individual/Personal'),
        ('business', 'Business/Company')
    ], validators=[DataRequired()])
    business_phone = StringField('Business Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Business Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    submit = SubmitField('Complete Registration')

class MpesaCredentialsForm(FlaskForm):
    """Form for M-Pesa API credentials setup."""
    consumer_key = StringField('Consumer Key', validators=[DataRequired()])
    consumer_secret = StringField('Consumer Secret', validators=[DataRequired()])
    business_shortcode = StringField('Business Shortcode', validators=[DataRequired()])
    passkey = StringField('Passkey', validators=[DataRequired()])
    callback_url = StringField('Callback URL', validators=[DataRequired()])
    environment = SelectField('Environment', choices=[
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production (Live)')
    ], validators=[DataRequired()])
    submit = SubmitField('Save M-Pesa Credentials')

class ResetPasswordRequestForm(FlaskForm):
    """Form to request a password reset."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Form to reset password."""
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
