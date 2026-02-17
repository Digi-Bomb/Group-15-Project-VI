from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices
from data_validator import DataValidator
from time_manager import TimeManager

class BookingService:
    def __init__(self, database: DatabaseConnection, validator: DataValidator, time_manager: TimeManager):
        self.database = database
        self.validator = validator
        self.time_manager = time_manager

    def create_booking(
        self,
        meeting_date: str,
        start_time: str,
        duration: str,
        meeting_owner: str,
        meeting_room: str,
        meeting_capacity: int,
    ):
        db = DatabaseConnection()
        reader = DatabaseReadingServices(db)
        writer = DatabaseWritingServices(db, reader)
        
        create_booking = writer.create_new_booking(
            meeting_date=meeting_date,
            start_time=start_time,
            duration=duration,
            meeting_owner=meeting_owner,
            meeting_room=meeting_room,
            meeting_capacity=meeting_capacity
        )
        return create_booking
