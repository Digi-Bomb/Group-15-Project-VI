from flask import Blueprint, render_template, request, redirect, session, g, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from forms import RegisterForm, LoginForm, LogoutForm
from database_connection import get_db

account_bp = Blueprint('account', __name__)

#TODO:
#create account info display page


@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
        except mysql.connector.Error as e:
            current_app.logger.error(f"DB error: {e}")
            flash("Registration failed.", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect('/login')
    return render_template('register.html', form=form)


@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s",
            (form.username.data,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], form.password.data):
            session.permanent = True
            session['user_id'] = user[0]
            return redirect('/')

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
