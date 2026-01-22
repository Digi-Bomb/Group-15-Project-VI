from flask import Flask, render_template, request, redirect, session, g, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Regexp
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import timedelta
import mysql.connector
import time

# i copy/pasted the imports that i used from the softsec project
# wtforms helped manage user input validation and database storage stuff
# limiter helped with rate limiting to prevent brute force / DoS (not sure if itll mess up our testing)
# can remove or add any as needed

# -- CONFIG -- 

app = Flask(__name__)
app.config["WTF_CSRF_ENABLED"] = True #CSRF defense

#session cookie setup - change for prod
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, #prevents JavaScript access to cookie data
    SESSION_COOKIE_SECURE=False,  #true if https, recommended for prod
    SESSION_COOKIE_SAMESITE="Lax" 
    # lax allows external links to use GET index of this site if clicked
    # but prevents some CSRF attacks by limiting how other sites can use session cookie
)


#secret key setup for session cookies 
secret = os.environ.get("SECRET_KEY")
if secret:
    app.secret_key = secret
else:
    app.secret_key = os.urandom(24)
    #only use if env var fails, non persistent sessions if app restarts

#rate limiter - global default
limiter = Limiter(
    key_func=get_remote_address,     #client IP
    app=app,                        
    default_limits=["100 per hour"],  #global limit
)

#logging setup
if not os.path.exists('logs'):
    os.mkdir('logs')

#general log
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3) #keep 3 latest logs
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

#error log
error_handler = RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=3)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))

error_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)
app.logger.addHandler(error_handler)
app.logger.setLevel(logging.INFO)

app.logger.info('Flask app startup')

#session timeout set up - end session after 15 minutes without activity
app.permanent_session_lifetime = timedelta(minutes=15)

#refresh session timer with activity
@app.before_request
def make_session_permanent():
    session.permanent = True 

#load logout form
@app.before_request
def add_logout_form():
    g.logout_form = LogoutForm()

# -- FORMS -- 

#define forms for Flask-WTF - avoid CSRF, validate input

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

# -- ROUTES -- 

def get_db():
    for _ in range(5):
        try:
            return mysql.connector.connect(
                host=os.environ.get("MYSQL_HOST", "localhost"),
                user=os.environ.get("MYSQL_USER"),
                password=os.environ.get("MYSQL_PASSWORD"),
                database=os.environ.get("MYSQL_DATABASE"),
            )
        except mysql.connector.Error:
            time.sleep(2)
    app.logger.error("Could not connect to MySQL after retries")
    raise

#lower rate limit for commonly abused routes
#@limiter.limit("5 per minute")
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm() #using register form
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data) #generate password hash before transport
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute( #adjust table name/attributes to the final db schema
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
        except mysql.connector.Error as e:
            app.logger.error(f"DB error: {e}")
            flash("Registration failed.", "danger")
        finally:
            cursor.close()
            conn.close()

        return redirect("/login")

    return render_template("register.html", form=form)

@limiter.limit("5 per minute")
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm() #using login form
    if form.validate_on_submit():
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute( #adjust to db schema
            "SELECT id, username, password FROM users WHERE username = %s",
            (form.username.data,)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], form.password.data):
            session.permanent = True
            session["user_id"] = user[0]
            return redirect("/notes")
        else:
            flash("Invalid username or password.", "danger")
            app.logger.warning(
                f"Failed login attempt for username: {form.username.data}"
            )

    return render_template("login.html", form=form)

@app.route("/logout", methods=["POST"])
def logout():
    form = g.logout_form
    if form.validate_on_submit():
        user_id = session.get("user_id")
        session.clear()
        flash("Logged out successfully.", "success")
        app.logger.info(f"User {user_id} logged out")
    return redirect("/")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
