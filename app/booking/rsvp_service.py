from database_connection import DatabaseConnection
from notifications.email_notification_service import EmailNotificationService

class AccountService:
    def __init__(self, database: DatabaseConnection, notification_service: EmailNotificationService):
        self.database = database
        self.notification_service = notification_service
