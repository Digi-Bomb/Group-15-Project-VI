from flask import Blueprint, render_template, request, redirect, session, g, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm, LogoutForm
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices


## @brief Blueprint for account-related routes
account_bp = Blueprint("account", __name__)


@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed")
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data

        createUser = writer.create_new_user(username, email, firstName, lastName, password)
        #can confirm user creation with createUser boolean, flash message accordingly
        print(createUser)
        print("^createUser result")
        if createUser[0]:
            flash("Registration successful! Please log in.", "success")
        else:
            flash("Registration failed. User may already exist.", "danger")
        return redirect("/login")
    return render_template("register.html", form=form)


@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data #
        #validate_user_information returns a tuple (boolean, message) where boolean indicates success of login and message provides additional context
        try:
            ok, user_id = reader.validate_user_information(username=user, password=password)
        except RuntimeError:
            flash("Login temporarily unavailable (database offline).", "danger")
            return render_template("login.html", form=form)

        if ok:  # loginUser returns a tuple (boolean, message)
            session.permanent = True
            session["user_id"] = user_id# Assuming loginUser[1] contains the user_id
            return redirect("/")

        flash('Invalid username or password.', 'danger')
        current_app.logger.warning(f"Failed login attempt for username: {form.username.data}")

    return render_template('login.html', form=form)


@account_bp.route('/logout', methods=['POST'])
def logout():
    form = LogoutForm()  # create new logout form instance to validate CSRF token
    if not form.validate_on_submit():
        flash("Invalid logout request.", "danger")
        return redirect('/')

    user_id = session.get('user_id')
    session.clear()
    flash('Logged out successfully.', 'success')
    current_app.logger.info(f"User {user_id} logged out")
    return redirect('/')

@account_bp.route("/profile")
def profile():
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    # Check if user is logged in
    user_id = session.get("user_id")
    # if not user_id:
    #    flash("You must log in to view your profile.", "warning")
    #    return redirect("/login")

    # Fetch user info from the database
    #TODO: NEEDS ACTUAL ROUTE PLEASE!!!!!!!!!!
    cursor = reader.conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT username, email FROM RegisteredUser WHERE RUID = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()

    # if not user:
    #    flash("User not found.", "danger")
    #    return redirect("/login")

    return render_template("profile.html", user=user)
