from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Regexp

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20), Regexp(r'^\w+$', message="Username must contain only letters, numbers, or underscores")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    #confirm matching passwords
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match")
    ])
    submit = SubmitField("Register")

    #check unique username before registering
    #avoid sharing data between users that share username
    def validate_username(self, field):
        from app.database_connection import get_db
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (field.data,)
        )
        existing = cursor.fetchone()

        cursor.close()
        conn.close()

        if existing:
            raise ValidationError("Username already exists.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class NoteForm(FlaskForm):
    note = TextAreaField("Note", validators=[DataRequired(), Length(max=500)]) #max 500 characters for now
    submit = SubmitField("Add Note")


class LogoutForm(FlaskForm):
    submit = SubmitField("Logout")
