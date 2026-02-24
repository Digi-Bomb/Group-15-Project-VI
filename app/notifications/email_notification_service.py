"""!
@file email_notification_service.py
@brief Email notification utilities for booking events (reminders, updates, RSVP activity).

This module centralizes all outgoing email behavior for the Room Booking Web Application.
It relies on Flask-Mail for SMTP delivery and uses the database services to discover
recipients associated with a booking.

@note This service imports the Flask-Mail `mail` instance lazily inside
      send_email_notification() to avoid circular imports with app.py.
"""

import re

from booking.booking import Booking
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices

from flask import redirect, flash, current_app
from flask_mail import Message
from audit_logging.audit_logger import AuditLogger
from time_manager import TimeManager

class EmailNotificationService:
    """!
    @brief Sends booking-related email notifications.
    
    The service wraps:
    - Recipient discovery (registered + unregistered attendees)
    - Message composition for reminder/update/delete scenarios
    - Audit logging for notification attempts and outcomes
    
    @param database DatabaseConnection used by reading/writing service layers.
    """
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.database_reading_services = DatabaseReadingServices(database)
        self.database_writing_services = DatabaseWritingServices(database, self.database_reading_services)

    # def send_email_notification(self, recipient_email: str, subject: str, body: str) -> bool:
    #     #to avoid circular import, import mail here, when we need it
    #     from app import mail
    #     sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
    #     audit_logger = AuditLogger()
    #     audit_logger.log_audit_event(f"Attempting to send email notification to {recipient_email} with subject '{subject}'.")
    #     if not recipient_email or not sender_email:
    #         current_app.logger.error("Recipient or sender email not configured")
    #         audit_logger.log_audit_event(f"Failed to send email notification to {recipient_email} due to missing email configuration.")
    #         flash("Email configuration missing.", "error")
    #         return False

    #     try:
    #         msg = Message(
    #             subject=subject,
    #             sender=sender_email,
    #             recipients=[recipient_email],
    #             body=body
    #         )
    #         mail.send(msg)  # send using the instance imported from app.py
    #         audit_logger.log_audit_event(f"Sent email notification to {recipient_email} with subject '{subject}'.")
    #         return True
    #     except (ConnectionError, TimeoutError, OSError) as e:
    #         current_app.logger.error(f"Mail send failed: {e}", exc_info=True)
    #         audit_logger.log_audit_event(f"Failed to send email notification to {recipient_email} due to error: {e}")
    #         flash("Failed to send email.", "error")
    #         return False

    def send_email_notification(self, recipient_email: str | list, subject: str, body: str) -> bool:
        #to avoid circular import, import mail here, when we need it
        from app import mail
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        audit_logger = AuditLogger()

        # Convert string to list if needed
        if isinstance(recipient_email, str):
            recipients = [recipient_email]
        else:
            recipients = recipient_email

        audit_logger.log_audit_event(f"Attempting to send email notification to {recipients} with subject '{subject}'.")

        if not recipients or not sender_email:
            current_app.logger.error("Recipient or sender email not configured")
            audit_logger.log_audit_event(f"Failed to send email notification to {recipients} due to missing email configuration.")
            flash("Email configuration missing.", "error")
            return False

        try:
            msg = Message(
                subject=subject,
                sender=sender_email,
                recipients=recipients,
                body=body
            )
            mail.send(msg)
            audit_logger.log_audit_event(f"Sent email notification to {recipients} with subject '{subject}'.")
            return True
        except (ConnectionError, TimeoutError, OSError) as e:
            current_app.logger.error(f"Mail send failed: {e}", exc_info=True)
            audit_logger.log_audit_event(f"Failed to send email notification to {recipients} due to error: {e}")
            flash("Failed to send email.", "error")
            return False

    def send_new_rsvp_notification_email(self, booking_owner_id: int, attendee_name: str, booking_id: int):

        """!

        @brief Notify the booking owner that a new attendee RSVP'd.

        @param booking_owner_id Registered user ID (RUID) of the booking owner.

        @param attendee_name Display name of the attendee who RSVP'd.

        @param booking_id Booking identifier that was RSVP'd to.

        """
        audit_logger = AuditLogger()
        meeting_owner_email = self.database_reading_services.get_registered_user_email_from_RUID(booking_owner_id)
        self.send_email_notification(meeting_owner_email, "New Booking RSVP", f"{attendee_name} has RSVP'd to your booking: '{booking_id}'.")

        audit_logger.log_audit_event(f"Sent new RSVP confirmation notification email to {meeting_owner_email} for booking ID {booking_id} due to new RSVP confirmation from {attendee_name}.")

    def send_booking_notification_email(self, booking: Booking):

        """!

        @brief Send a reminder email to all attendees for an upcoming booking.

        @param booking Booking domain object containing schedule and location info.

        

        @post Sets booking.reminder_sent = True and persists reminder state in the database.

        """
        recipent_list = []
        audit_logger = AuditLogger()

        for unregistered_user in self.database_reading_services.get_unregistered_users_associated_with_booking_ID(booking.booking_id):
            recipent_list.append(self.database_reading_services.get_unregistered_user_email_from_URUID(unregistered_user.URUID))

        for registered_user in self.database_reading_services.get_registered_users_associated_with_booking_ID(booking.booking_id):
            recipent_list.append(self.database_reading_services.get_registered_user_email_from_RUID(registered_user.RUID))

        self.send_email_notification(recipent_list, "Reminder: Upcoming Booking", f"Your booking is scheduled for {booking.start_time} - {booking.end_time} at {booking.location}.")

        audit_logger.log_audit_event(f"Sent booking reminder notification email to {recipent_list} for booking ID {booking.booking_id}.")

        booking.reminder_sent = True
        self.database_writing_services.update_booking_reminder_sent(booking.booking_id)

    def send_booking_update_notification_email(self, booking_id: int):

        """!

        @brief Notify attendees that a booking was updated and prompt them to RSVP again.

        @param booking_id Booking identifier to fetch and notify for.

        

        @note If attendee count <= 1, no notification is sent (owner-only booking).

        """
        audit_logger = AuditLogger()
        recipent_list = []

        booking_info = self.database_reading_services.get_booking_information_of_specific_booking(booking_id)

        if booking_info[4] <= 1:
            return

        for unregistered_user in self.database_reading_services.get_unregistered_users_associated_with_booking_ID(booking_id):
            email = self.database_reading_services.get_unregistered_user_email_from_URUID(unregistered_user[0])
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if re.match(pattern, email) and email not in recipent_list:
                recipent_list.append(email)

        end_time = TimeManager.get_end_time_from_start_time_and_duration(booking_info[2], booking_info[3])
        end_time = TimeManager.timedelta_to_time(end_time)

        self.send_email_notification(recipent_list, "Booking Updated", f"Your booking has been updated. Date: {booking_info[1]} Time: {booking_info[2]} - End Time: {end_time} Room: {booking_info[0]}. Please RSVP again if you are still attending at this link: http://localhost:5000/rsvp/{booking_info[7]}")
        audit_logger.log_audit_event(f"Sent booking update notification email to {recipent_list} for booking ID {booking_id}.")

    def send_booking_delete_notification_email(self, booking_id: int):

        """!

        @brief Notify attendees that a booking was deleted.

        @param booking_id Booking identifier to fetch and notify for.

        

        @note If attendee count <= 1, no notification is sent (owner-only booking).

        """
        audit_logger = AuditLogger()
        recipent_list = []

        booking_info = self.database_reading_services.get_booking_information_of_specific_booking(booking_id)

        if booking_info[4] <= 1:
            return

        for unregistered_user in self.database_reading_services.get_unregistered_users_associated_with_booking_ID(booking_id):
            email = self.database_reading_services.get_unregistered_user_email_from_URUID(unregistered_user[0])
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if re.match(pattern, email) and email not in recipent_list:
                recipent_list.append(email)

        end_time = TimeManager.get_end_time_from_start_time_and_duration(booking_info[2], booking_info[3])
        end_time = TimeManager.timedelta_to_time(end_time)

        self.send_email_notification(recipent_list, "Booking Deleted", f"Your booking has been deleted. Date: {booking_info[1]} Time: {booking_info[2]} - End Time: {end_time} Room: {booking_info[0]}.")
        audit_logger.log_audit_event(f"Sent booking delete notification email to {recipent_list} for booking ID {booking_id}.")
