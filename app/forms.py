from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, TimeField, DateField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Regexp


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20), Regexp(r'^\w+$', message="Username must contain only letters, numbers, or underscores")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    firstName = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    lastName = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Length(max=120), Regexp(r'^[\w\.-]+@[\w\.-]+\.\w+$', message="Invalid email address")])
    #confirm matching passwords
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match")
    ])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class NoteForm(FlaskForm):
    note = TextAreaField("Note", validators=[DataRequired(), Length(max=500)]) #max 500 characters for now
    submit = SubmitField("Add Note")


class LogoutForm(FlaskForm):
    submit = SubmitField("Logout")

#create booking form
class BookingForm(FlaskForm):
    meeting_date = DateField("Meeting Date", validators=[DataRequired()])
    start_time = TimeField("Start Time", format="%H:%M", validators=[DataRequired()])
    end_time = TimeField("End Time", format="%H:%M", validators=[DataRequired()])
    meeting_capacity = SelectField("Capacity", coerce=int)
    submit = SubmitField()
