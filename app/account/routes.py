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
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        firstName = form.firstName.data
        lastName = form.lastName.data
        email = form.email.data

        createUser = DatabaseWritingServices.create_new_user(username, email, firstName, lastName, password)
        #can confirm user creation with createUser boolean, flash message accordingly
        if createUser:
            flash("Registration successful! Please log in.", "success")
        else:
            flash("Registration failed. User may already exist.", "danger")

        return redirect("/login")
    return render_template("register.html", form=form)


@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        #user submits plaintext password, we hash it and compare to the hash in the database
        user = form.username.data
        #ISSUE - change this to pull the hash from the database and compare with check_password_hash, currently just hashing the input and comparing to the hash in the database which is not correct
        password = generate_password_hash(form.password.data)

        loginUser = DatabaseReadingServices.validate_user_information(username=user, password=password)

        if loginUser[0]:  # loginUser returns a tuple (boolean, message)
            session.permanent = True
            session["user_id"] = loginUser[1]  # Assuming loginUser[1] contains the user_id
            return redirect("/")

        flash('Invalid username or password.', 'danger')
        current_app.logger.warning(f"Failed login attempt for username: {form.username.data}")

    return render_template('login.html', form=form)


@account_bp.route('/logout', methods=['POST'])
def logout():
    form = g.logout_form
    if form.validate_on_submit():
        user_id = session.get('user_id')
        session.clear()
        flash('Logged out successfully.', 'success')
        current_app.logger.info(f"User {user_id} logged out")
    return redirect('/')
