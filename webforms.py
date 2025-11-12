from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField , SubmitField , BooleanField , DateField
from wtforms.validators import DataRequired ,EqualTo , ValidationError


# userform 
class UserForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    username = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired(), EqualTo('confirm_password', message = 'Passwords Must Match!!')])
    confirm_password =PasswordField("Confirm Password",validators=[DataRequired()])
    agree_to_terms = BooleanField('I Agree to terms and conditions ' , validators=[DataRequired()])
    submit = SubmitField(("submit"))


# login form
class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])    
    password =PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField(("submit"))
    
class BookingForm(FlaskForm):
    country = StringField("Country : " , validators=[DataRequired()])
    place = StringField("Place To Travel : " , validators=[DataRequired()])
    date_of_trip =  DateField("Date Of Journey :" , validators=[DataRequired()])
    guide = BooleanField("Need a Guide ? ",validators=[DataRequired()],default=False)
    guide_lang = StringField("Guide Language :")
    agree_to_terms = BooleanField("Agree To Terms",validators=[DataRequired()])
    submit = SubmitField("Confirm Your Booking")
    
    