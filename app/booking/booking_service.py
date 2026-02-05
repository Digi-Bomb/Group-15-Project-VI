from app.database_connection import DatabaseConnection
from app.data_validator import DataValidator
from app.time_manager import TimeManager

class BookingService:
    def __init__(self, database: DatabaseConnection, validator: DataValidator, time_manager: TimeManager):
        self.database = database
        self.validator = validator
        self.time_manager = time_manager
