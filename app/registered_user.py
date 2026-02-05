from typing import List
from booking import Booking


class RegisteredUser:
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def validate_credentials(self, password: str) -> bool:
        return False

    def get_bookings(self) -> List[Booking]:  # Testing for colin branch
        return []
