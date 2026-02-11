from database_connection import DatabaseConnection

from flask import redirect, flash, current_app
from flask_mail import Message

class EmailNotificationService:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        
    def send_email_notification(self, recipient_email: str, subject: str, body: str) -> bool:
        #to avoid circular import, import mail here, when we need it
        from app import mail
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

        if not recipient_email or not sender_email:
            current_app.logger.error("Recipient or sender email not configured")
            flash("Email configuration missing.", "error")
            return False

        try:
            msg = Message(
                subject=subject,
                sender=sender_email,
                recipients=[recipient_email],
                body=body
            )
            mail.send(msg)  # send using the instance imported from app.py
            flash("Email sent successfully!", "success")
            return True
        except (ConnectionError, TimeoutError, OSError) as e:
            current_app.logger.error(f"Mail send failed: {e}", exc_info=True)
            flash("Failed to send email.", "error")
            return False
    
    def send_booking_notification_email(self, booking_owner_id: int, attendee_name: str, booking_id: int):
        self.send_email_notification("", "New Booking RSVP", f"{attendee_name} has RSVP'd to your booking: '{booking_id}'.")
        pass