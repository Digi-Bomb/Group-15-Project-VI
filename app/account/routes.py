## @package app.account.routes
# @brief Account authentication routes module
# 
# This module defines Flask routes for account management including
# user registration, login, and logout functionality.

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    g,
    flash,
    current_app,
)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from forms import RegisterForm, LoginForm, LogoutForm
from database_connection import DatabaseConnection

## @brief Blueprint for account-related routes
account_bp = Blueprint("account", __name__)

# TODO:
# create account info display page (accountservice method to get user info by id, route to render template with this info)


## @brief Handle user registration
# @details
# Handles both GET requests to display the registration form and POST requests
# to process new user registration. Validates form data and inserts new user
# into the RegisteredUser table in the database.
# @return Rendered registration template on GET or login redirect on successful POST
@account_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        firstName = form.firstName.data
        lastName = form.lastName.data
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO RegisteredUser (username, pass, firstName, lastName) VALUES (%s, %s, %s, %s)",
                (username, password, firstName, lastName),
            )
            conn.commit()
        except mysql.connector.Error as e:
            current_app.logger.error(f"DB error: {e}")
            flash("Registration failed.", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect("/login")
    return render_template("register.html", form=form)

## @brief Handle user login authentication
# @details
# Handles both GET requests to display the login form and POST requests
# to authenticate user credentials. Verifies username and password against
# the database and establishes a session if credentials are valid.
# @return Rendered login template on GET or home redirect on successful POST
@account_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, pass FROM RegisteredUser WHERE username = %s",
            (form.username.data,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], form.password.data):
            session.permanent = True
            session["user_id"] = user[0]
            return redirect("/")

        flash("Invalid username or password.", "danger")
        current_app.logger.warning(
            f"Failed login attempt for username: {form.username.data}"
        )

    return render_template("login.html", form=form)


## @brief Handle user logout
# @details
# Clears the user session and logs out the current user.
# Requires a valid logout form submission.
# @return Redirect to home page after logout
@account_bp.route("/logout", methods=["POST"])
def logout():
    form = g.logout_form
    if form.validate_on_submit():
        user_id = session.get("user_id")
        session.clear()
        flash("Logged out successfully.", "success")
        current_app.logger.info(f"User {user_id} logged out")
    return redirect("/")
