from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SettingsForm(FlaskForm):
    """Form for updating user and business settings."""
    # User fields
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])

    # Business fields
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=120)])
    business_phone = StringField('Business Phone', validators=[DataRequired(), Length(max=20)])
    business_address = StringField('Address', validators=[Length(max=200)])
    business_city = StringField('City', validators=[Length(max=100)])
    business_country = StringField('Country', validators=[Length(max=100)])
    
    # Logo upload
    business_logo = FileField('Business Logo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])

    submit = SubmitField('Save Changes')
