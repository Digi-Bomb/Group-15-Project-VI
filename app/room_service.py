from database_connection import DatabaseConnection

class RoomService:
    def __init__(self, database: DatabaseConnection):
        self.database = database