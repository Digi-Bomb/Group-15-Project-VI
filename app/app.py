from flask import Flask, render_template, request, redirect, session, g, flash
from flask import request

from forms import RegisterForm, LoginForm, NoteForm, LogoutForm
from werkzeug.security import generate_password_hash, check_password_hash

import database_connection
import database_reading
import database_writing

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import logging
from logging.handlers import RotatingFileHandler

from flask_mail import Mail, Message

from flask_apscheduler import APScheduler


import os
from datetime import timedelta, date, time


# -- CONFIG --
mail = Mail()
app = Flask(__name__)
app.config["WTF_CSRF_ENABLED"] = True  # CSRF defense

# session cookie setup - change for prod
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,  # prevents JavaScript access to cookie data
    SESSION_COOKIE_SECURE=False,  # true if https, recommended for prod
    SESSION_COOKIE_SAMESITE="Lax",
    # lax allows external links to use GET index of this site if clicked
    # but prevents some CSRF attacks by limiting how other sites can use session cookie
)

# mail setup - using Gmail SMTP for demo, change for prod
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("DEL_EMAIL")
app.config["MAIL_USERNAME"] = os.environ.get("DEL_EMAIL")
app.config["MAIL_PASSWORD"] = os.environ.get("DEL_EMAIL_PASSWORD")
app.config["REC_EMAIL"] = os.environ.get("REC_EMAIL")


# secret key setup for session cookies
secret = os.environ.get("SECRET_KEY")
if secret:
    app.secret_key = secret
else:
    app.secret_key = os.urandom(24)
    # only use if env var fails, non persistent sessions if app restarts

# rate limiter - global default
limiter = Limiter(
    key_func=get_remote_address,  # client IP
    app=app,
    default_limits=["100 per hour"],  # global limit
)

# logging setup
if not os.path.exists("logs"):
    os.mkdir("logs")

# general log
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10240, backupCount=3
)  # keep 3 latest logs
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
)
file_handler.setLevel(logging.INFO)

# error log
error_handler = RotatingFileHandler("logs/error.log", maxBytes=10240, backupCount=3)
error_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
)

error_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)
app.logger.addHandler(error_handler)
app.logger.setLevel(logging.INFO)

app.logger.info("Flask app startup")

# session timeout set up - end session after 15 minutes without activity
app.permanent_session_lifetime = timedelta(minutes=15)


# refresh session timer with activity
@app.before_request
def make_session_permanent():
    session.permanent = True


# load logout form
@app.before_request
def add_logout_form():
    g.logout_form = LogoutForm()


# context processor for navbar
@app.context_processor
def inject_user():
    return dict(user_id=session.get("user_id"), is_logged_in=("user_id" in session))


# Forms are defined in app/forms.py and imported above

# once config is loaded, initialize mail extension
mail.init_app(app)

testpass = generate_password_hash("PassW0rd")
# test = database_reader.return_all_bookings_for_a_user(1005)
# createBooking = database_writing.DatabaseWritingServices(
#     databaseConn, database_reader
# ).create_new_user('test2', 'test2','','',testpass)


# testAddBID = testAddBID[1]
# if testAddBID == 0:
#     test2 = database_writing.DatabaseWritingServices(
#         databaseConn, database_reader
#     ).associate_unregistered_user_with_booking(testAddBID, 1000)

# test = database_reading.DatabaseReadingServices(
#     database_connection.DatabaseConnection()
# ).get_username_via_RUID("1000")
# print(test)
# -- ROUTES --
from account.routes import account_bp
from booking.routes import booking_bp
from notifications.routes import notifications_bp, send_booking_notification_emails
from audit_logging.audit_logger import AuditLogger

# register blueprints
app.register_blueprint(account_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(notifications_bp)


@app.route("/", methods=["GET"])
def index():
    db = database_connection.DatabaseConnection()
    reader = database_reading.DatabaseReadingServices(db)

    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = date.today().isoformat()

    rooms = reader.get_rooms()
    
    user_id = session.get("user_id")

    # if a user is logged in, display their bookings at the top
    if user_id:
        my_bookings = reader.return_all_bookings_with_info_for_a_user(user_id)
        return render_template("index.html", rooms=rooms, selected_date=selected_date, bookings=my_bookings, user=user_id)

    return render_template("index.html", rooms=rooms, selected_date=selected_date)


if __name__ == "__main__":
    audit_logger = AuditLogger()
    scheduler = APScheduler()
    scheduler.add_job(func=send_booking_notification_emails, trigger='interval', id='job', seconds=5)
    scheduler.start()
    audit_logger.log_audit_event("started long log.")
    audit_logger.log_short_term("started short log.")
    app.run(debug=True, host="0.0.0.0", port=5000)
