from booking.booking import Booking
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices

from flask import redirect, flash, current_app
from flask_mail import Message

class EmailNotificationService:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.database_reading_services = DatabaseReadingServices(database)
        
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
    
    def send_new_rsvp_notification_email(self, booking_owner_id: int, attendee_name: str, booking_id: int):
        meeting_owner_email = self.database_reading_services.get_registered_user_email_from_RUID(booking_owner_id)
        self.send_email_notification(meeting_owner_email, "New Booking RSVP", f"{attendee_name} has RSVP'd to your booking: '{booking_id}'.")
        
        from ..app import audit_logger
        audit_logger.log_long_term(f"Sent new RSVP confirmation notification email to {meeting_owner_email} for booking ID {booking_id} due to new RSVP confirmation from {attendee_name}.")
        
    def send_booking_notification_email(self, booking: Booking):
        recipent_list = []
                
        for unregistered_user in self.database_reading_services.get_registered_users_associated_with_booking_ID(booking.booking_id):
            recipent_list.append(unregistered_user)
        
        for registered_user in self.database_reading_services.get_registered_users_associated_with_booking_ID(booking.booking_id):
            recipent_list.append(self.database_reading_services.get_registered_user_email_from_RUID(registered_user.RUID))
            
        self.send_email_notification(recipent_list, "Reminder: Upcoming Booking", f"Your booking '{booking.booking_name}' is scheduled for {booking.start_time} - {booking.end_time} at {booking.location}.")
        
        from ..app import audit_logger
        audit_logger.log_long_term(f"Sent booking reminder notification email to {recipent_list} for booking ID {booking.booking_id}.")
        
        booking.reminder_sent = True
        self.database_reading_services.set_send_reminder_email_flag_for_booking(booking.booking_id, True)