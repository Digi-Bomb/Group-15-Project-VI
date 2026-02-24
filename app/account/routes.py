"""
@file routes.py
@brief Account blueprint routes for registration, login, logout, and profile viewing.
@details
This module defines the Flask Blueprint responsible for account-related endpoints:
- Register (GET/POST)
- Login (GET/POST)
- Logout (POST)
- Profile (GET)

The routes use:
- WTForms (RegisterForm, LoginForm, LogoutForm)
- Database services (DatabaseConnection, DatabaseReadingServices, DatabaseWritingServices)
- AuditLogger for security/audit events

Authentication model:
- Session-based login using session["user_id"].
"""

from flask import Blueprint, render_template, request, redirect, session, g, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm, LogoutForm
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices
from audit_logging.audit_logger import AuditLogger
from time_manager import TimeManager

## @brief Blueprint for account-related routes.
## @details All account/auth endpoints are registered under this blueprint.
account_bp = Blueprint("account", __name__)


@account_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    @brief Register a new user account.
    @details
    - GET: Render the registration form.
    - POST: Validate submitted form, hash password, and attempt to create the user.
      On success, redirects to login. On failure (e.g., duplicate username/email),
      flashes an error and redirects to login.

    Form fields:
    - username
    - password (hashed before storing)
    - firstName
    - lastName
    - email

    Side effects:
    - Inserts new user in DB via writer.create_new_user().
    - Writes audit log events.
    - Uses flash messages and redirect for flow control.

    @return
    - GET: Rendered "register.html"
    - POST: Redirect to "/login" (with success/failure flash message)
    """
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)
    form = RegisterForm()
    audit_logger = AuditLogger()

    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data

        createUser = writer.create_new_user(username, email, firstName, lastName, password)

        if createUser[0]:
            audit_logger.log_audit_event(
                "User registered",
                f"Successfully registered user: (username: {username}, email: {email}, firstName: {firstName}, lastName: {lastName})",
            )
            flash("Registration successful! Please log in.", "success")
        else:
            audit_logger.log_audit_event(
                "User registration failed",
                f"Failed to register user: {username} (username may already exist)",
            )
            flash("Registration failed. User may already exist.", "danger")

        return redirect("/login")

    return render_template("register.html", form=form)


@account_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    @brief Authenticate a user and begin a session.
    @details
    - GET: Render login form.
    - POST: Validate form, verify credentials via reader.validate_user_information().
      On success, sets session["user_id"] and redirects to home.
      On failure, flashes an error and re-renders login template.

    Error handling:
    - If reader.validate_user_information raises RuntimeError (e.g., DB offline),
      logs an audit event and renders login with a "temporarily unavailable" message.

    Side effects:
    - Sets session.permanent = True on successful login.
    - Writes audit log events.
    - Writes app log warnings for failed login.

    @return
    - GET: Rendered "login.html"
    - POST success: Redirect to "/"
    - POST failure: Rendered "login.html" with flash message
    """
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    form = LoginForm()
    audit_logger = AuditLogger()

    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data

        try:
            ok, msg, user_id = reader.validate_user_information(username=user, password=password)
        except RuntimeError:
            audit_logger.log_audit_event(
                "Login failed - database error",
                f"Login attempt for username: {user} failed due to database is offline.",
            )
            flash("Login temporarily unavailable (database offline).", "danger")
            return render_template("login.html", form=form)

        if ok:
            session.permanent = True
            session["user_id"] = user_id
            audit_logger.log_audit_event("Login successful", f"Successful login for user: {user}")
            return redirect("/")

        audit_logger.log_audit_event(
            "Login failed - invalid credentials",
            f"Failed login attempt for username: {user} with provided password.",
        )
        flash("Invalid username or password.", "danger")
        current_app.logger.warning(f"Failed login attempt for username: {form.username.data}")

    return render_template("login.html", form=form)


@account_bp.route("/logout", methods=["POST"])
def logout():
    """
    @brief Log the current user out and clear their session.
    @details
    Validates CSRF via LogoutForm. If CSRF validation fails, logs an audit event,
    flashes an error, and redirects to home. On success, clears session and redirects.

    Security:
    - CSRF protection is enforced using LogoutForm.validate_on_submit().

    Side effects:
    - Clears session state (session.clear()).
    - Writes audit log events.
    - Writes app logs.

    @return Redirect to "/".
    """
    form = LogoutForm()  # create new logout form instance to validate CSRF token
    audit_logger = AuditLogger()

    if not form.validate_on_submit():
        audit_logger.log_audit_event(
            "Logout failed - invalid CSRF token",
            "Invalid logout attempt due to failed CSRF validation.",
        )
        flash("Invalid logout request.", "danger")
        return redirect("/")

    user_id = session.get("user_id")
    session.clear()
    audit_logger.log_audit_event("Logout successful", f"User with ID {user_id} logged out successfully.")
    flash("Logged out successfully.", "success")
    current_app.logger.info(f"User {user_id} logged out")
    return redirect("/")


@account_bp.route("/profile")
def profile():
    """
    @brief Display the current user's profile page.
    @details
    Requires the user to be logged in (session["user_id"]).
    Fetches basic user details from the database and renders profile template.

    @note
    The query is executed directly via reader.conn.cursor(dictionary=True).
    Consider centralizing this in DatabaseReadingServices for consistency and testability.

    @return
    - If not logged in: redirect to "/login" with flash message.
    - If user not found: redirect to "/login" with flash message.
    - Otherwise: render "profile.html" with user context.
    """
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)

    user_id = session.get("user_id")
    if not user_id:
        flash("You must log in to view your profile.", "warning")
        return redirect("/login")

    cursor = reader.conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT username, email FROM RegisteredUser WHERE RUID = %s",
        (user_id,),
    )
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash("User not found.", "danger")
        return redirect("/login")

    return render_template("profile.html", user=user)
