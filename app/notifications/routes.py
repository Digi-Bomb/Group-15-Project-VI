from flask import Blueprint, request, redirect, flash, current_app
from flask_mail import Message

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    subject = request.form.get('subject')
    message = request.form.get('message')

    mail = current_app.extensions.get('mail')
    if mail:
        try:
            msg = Message(subject or 'Message from site', sender=current_app.config.get('MAIL_DEFAULT_SENDER'), recipients=[current_app.config.get('REC_EMAIL')])
            msg.body = f"Name: {name}\nSubject: {subject}\nMessage: {message}"
            mail.send(msg)
            return 'Email sent successfully!'
        except Exception as e:
            current_app.logger.error(f"Mail send failed: {e}")
            return str(e), 500

    flash('Mail subsystem not configured.', 'warning')
    return redirect('/')
