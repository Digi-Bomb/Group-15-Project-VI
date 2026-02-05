from database_connection import DatabaseConnection

class AccountService:
    def __init__(self, database: DatabaseConnection):
        self.database = database
