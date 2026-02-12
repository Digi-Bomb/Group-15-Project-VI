from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Regexp

from app.database_connection import get_db


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
    submit = SubmitField("Logout")

#create booking form
class BookingForm(FlaskForm):
    meeting_date = StringField("Meeting Date", validators=[DataRequired()])
    start_time = StringField("Start Time", validators=[DataRequired()])
    duration = StringField("Duration", validators=[DataRequired()])
    meeting_owner = StringField("Meeting Owner", validators=[DataRequired()])
    meeting_room = StringField("Meeting Room", validators=[DataRequired()])
    meeting_capacity = StringField("Meeting Capacity", validators=[DataRequired()])
    submit = SubmitField("Create Booking")
