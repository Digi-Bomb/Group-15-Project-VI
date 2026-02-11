## @package app.account.registered_user
# @brief Registered user module
#
# This module contains the RegisteredUser class which represents
# a registered user in the system with authentication and booking capabilities.

from typing import List
from booking import Booking


## @class RegisteredUser
# @brief Represents a registered user in the system
#
# Contains user profile information, credentials, and methods for
# credential validation and booking management.
class RegisteredUser:
    ## @brief Initialize a RegisteredUser instance
    # @param user_id Unique identifier for the user
    # @param username Username for login
    # @param email User's email address
    # @param password User's password (should be hashed)
    # @param first_name User's first name
    # @param last_name User's last name
    # @return None
    def __init__(self, user_id: int, username: str, email: str, password: str, first_name: str, last_name: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    ## @brief Validate user credentials
    # @param password Password to validate against stored credentials
    # @return True if password is valid, False otherwise
    def validate_credentials(self, password: str) -> bool:
        return False

    ## @brief Retrieve all bookings for this user
    # @return List of Booking objects associated with this user
    def get_bookings(self) -> List[Booking]:
        return []
