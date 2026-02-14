## @package app.account.unregistered_user
# @brief Unregistered user module
#
# This module contains the UnregisteredUser class which represents
# a guest or unregistered user in the system.

## @class UnregisteredUser
# @brief Represents an unregistered (guest) user in the system
#
# Contains basic guest user information without authentication credentials.
class UnregisteredUser:
    ## @brief Initialize an UnregisteredUser instance
    # @param unregistered_user_id Unique identifier for the unregistered user
    # @param nickname Nickname or display name for the guest user
    # @param email Guest user's email address
    # @return None
    def __init__(self, unregistered_user_id: int, nickname: str, email: str):
        self.unregistered_user_id = unregistered_user_id
        self.nickname = nickname
        self.email = email
