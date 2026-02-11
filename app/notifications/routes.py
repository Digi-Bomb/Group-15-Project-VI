from flask import Blueprint, request, redirect, flash, current_app
from flask_mail import Message

import datetime

from notifications.email_notification_service import EmailNotificationService
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/submit', methods=['POST'])
def submit():
    #to avoid circular import, import mail here, when we need it
    from app import mail

    name = request.form.get('name', '').strip() #strip whitespace, default to empty string if not provided
    subject = request.form.get('subject', 'No subject').strip()
    message = request.form.get('message', '').strip()

    if not message:
        flash("Message cannot be empty.", "warning")
        return redirect("/")

    recipient_email = current_app.config.get('REC_EMAIL')
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

    if not recipient_email or not sender_email:
        current_app.logger.error("Recipient or sender email not configured")
        flash("Email configuration missing.", "error")
        return redirect("/")

    try:
        msg = Message(
            subject=subject,
            sender=sender_email,
            recipients=[recipient_email]
        )
        msg.body = f"Name: {name}\nSubject: {subject}\nMessage: {message}"
        mail.send(msg)  # send using the instance imported from app.py
        flash("Email sent successfully!", "success")
        return redirect("/")
    except (ConnectionError, TimeoutError, OSError) as e:
        current_app.logger.error(f"Mail send failed: {e}", exc_info=True)
        flash("Failed to send email.", "error")
        return str(e), 500

def send_booking_notification_emails(self):
    all_bookings = DatabaseReadingServices(DatabaseConnection()).get_all_bookings()
    
    for booking in all_bookings:
        if not booking.reminder_sent:
            if booking.start_time - datetime.now() <= datetime.timedelta(minutes=30):
                EmailNotificationService(DatabaseConnection()).send_new_rsvp_notification_email(booking.booking_owner_id, "Reminder: Upcoming Booking", f"Your booking '{booking.booking_name}' is scheduled for {booking.start_time}.")
                