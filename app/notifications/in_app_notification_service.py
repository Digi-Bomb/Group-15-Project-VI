from database_connection import DatabaseConnection

class InAppNotificationService:
    def __init__(self, database: DatabaseConnection):
        self.database = database
