from database_connection import DatabaseConnection

class EmailNotificationService:
    def __init__(self, database: DatabaseConnection):
        self.database = database