from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DecimalField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class EditUserForm(FlaskForm):
    """Form for editing user details."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    password = PasswordField('New Password',
                           validators=[
                               Optional(),
                               Length(min=8, message='Password must be at least 8 characters long')
                           ],
                           render_kw={'placeholder': 'Leave blank to keep current password'})
    is_active = BooleanField('Active')
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Save Changes')

class UserRegistrationForm(FlaskForm):
    """Form for registering a new user."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    password = PasswordField('Password', 
                           validators=[
                               DataRequired(),
                               Length(min=8, message='Password must be at least 8 characters long')
                           ])
    password2 = PasswordField('Repeat Password', 
                             validators=[
                                 DataRequired(),
                                 EqualTo('password', message='Passwords must match')
                             ])
    is_active = BooleanField('Active', default=True)
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Register User')

class EditBusinessForm(FlaskForm):
    """Form for editing business details."""
    name = StringField('Business Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description')
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    address = StringField('Address', validators=[Length(max=200)])
    city = StringField('City', validators=[Length(max=100)])
    country = StringField('Country', validators=[Length(max=100)])
    logo = StringField('Logo URL')
    is_active = BooleanField('Active')
    submit = SubmitField('Save Changes')

class BusinessRegistrationForm(FlaskForm):
    """Form for registering a new business."""
    name = StringField('Business Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description')
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    address = StringField('Address', validators=[Length(max=200)])
    city = StringField('City', validators=[Length(max=100)])
    country = StringField('Country', validators=[Length(max=100)])
    owner_id = IntegerField('Owner User ID', validators=[Optional()])
    
    # M-Pesa API credentials
    mpesa_consumer_key = StringField('M-Pesa Consumer Key', validators=[Length(max=200)])
    mpesa_consumer_secret = StringField('M-Pesa Consumer Secret', validators=[Length(max=200)])
    mpesa_business_shortcode = StringField('Business Shortcode', validators=[Length(max=20)])
    mpesa_passkey = StringField('Passkey', validators=[Length(max=200)])
    mpesa_callback_url = StringField('Callback URL', validators=[Length(max=200)])
    mpesa_environment = SelectField('Environment', 
                                   choices=[
                                       ('sandbox', 'Sandbox (Testing)'),
                                       ('production', 'Production (Live)')
                                   ],
                                   default='sandbox')
    
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Register Business')

class SearchForm(FlaskForm):
    """Form for searching records."""
    search = StringField('Search', validators=[Optional()])
    status = SelectField('Status', 
                        choices=[
                            ('all', 'All'),
                            ('active', 'Active'),
                            ('inactive', 'Inactive')
                        ],
                        default='all')
    submit = SubmitField('Search')

class DateRangeForm(FlaskForm):
    """Form for date range selection."""
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Apply Filter')

class TransactionFilterForm(FlaskForm):
    """Form for filtering transactions."""
    status = SelectField('Status', 
                        choices=[
                            ('all', 'All Statuses'),
                            ('pending', 'Pending'),
                            ('completed', 'Completed'),
                            ('failed', 'Failed')
                        ],
                        default='all')
    business_id = SelectField('Business', coerce=int, default=0)
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Apply Filters')

class SettingsForm(FlaskForm):
    """Form for application settings."""
    site_name = StringField('Site Name', validators=[DataRequired()])
    items_per_page = IntegerField('Items Per Page', 
                                validators=[
                                    DataRequired(),
                                    NumberRange(min=1, max=100)
                                ],
                                default=10)
    
    # Email settings
    mail_server = StringField('Mail Server', validators=[DataRequired()])
    mail_port = IntegerField('Mail Port', 
                            validators=[
                                DataRequired(),
                                NumberRange(min=1, max=65535)
                            ])
    mail_use_tls = BooleanField('Use TLS')
    mail_username = StringField('Mail Username')
    mail_password = PasswordField('Mail Password')
    mail_default_sender = StringField('Default Sender', validators=[DataRequired(), Email()])
    
    # File upload settings
    upload_folder = StringField('Upload Folder', validators=[DataRequired()])
    max_content_length = IntegerField('Maximum File Size (bytes)',
                                    validators=[
                                        DataRequired(),
                                        NumberRange(min=1024)  # At least 1KB
                                    ])
    
    # Commission settings
    commission_rate = DecimalField('Commission Rate (%)', 
                                  places=2,
                                  validators=[
                                      DataRequired(),
                                      NumberRange(min=0, max=100)
                                  ])
    
    submit = SubmitField('Save Settings')
