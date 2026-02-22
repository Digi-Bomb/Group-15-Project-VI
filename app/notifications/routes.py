from flask import Blueprint, request, redirect, flash, current_app
from flask_mail import Message

import datetime

from notifications.email_notification_service import EmailNotificationService
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices

from audit_logging.audit_logger import AuditLogger

notifications_bp = Blueprint('notifications', __name__)

# def send_booking_notification_emails():
#     all_bookings = DatabaseReadingServices(DatabaseConnection()).get_all_bookings()
#     # print(all_bookings)
#     audit_logger = AuditLogger()
    
#     for booking_id in all_bookings:
        
#         booking_info = DatabaseReadingServices(DatabaseConnection()).get_booking_information_of_specific_booking(booking_id)
#         audit_logger.log_audit_event(booking_info)
#         if not booking_info[6]:
#             if booking_info[1] - datetime.now() <= datetime.timedelta(minutes=30):
#                 EmailNotificationService(DatabaseConnection()).send_booking_notification_email(booking_info[5], "Reminder: Upcoming Booking", f"Your booking in {booking_info[3]} is scheduled at {booking_info[1]} for {booking_info[2]}.")
#                 audit_logger.log_audit_event(f"Sent booking reminder notification email to {booking_info[5]} for booking ID {booking_id}.")