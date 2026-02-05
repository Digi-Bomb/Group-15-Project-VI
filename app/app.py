from flask import Flask, render_template, request, redirect, session, g, flash

from forms import RegisterForm, LoginForm, NoteForm, LogoutForm

from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import logging
from logging.handlers import RotatingFileHandler

from flask_mail import Mail, Message

import os
from datetime import timedelta
import time

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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get("DEL_EMAIL")
app.config['MAIL_PASSWORD'] = os.environ.get("DEL_EMAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("DEL_EMAIL")

mail = Mail(app)

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

# Forms are defined in app/forms.py and imported above

# -- ROUTES --
from app.account.routes import account_bp
from app.booking.routes import booking_bp
from app.notifications.routes import notifications_bp

# register blueprints
app.register_blueprint(account_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(notifications_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
