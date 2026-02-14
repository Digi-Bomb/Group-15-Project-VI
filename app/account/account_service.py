## @package app.account.account_service
# @brief Account service module
#
# This module contains the AccountService class which handles
# core account-related operations and database interactions.

from database_connection import DatabaseConnection

## @class AccountService
# @brief Service class for managing account operations
#
# Provides methods and utilities for account-related database operations
# and business logic.
class AccountService:
    ## @brief Initialize the AccountService
    # @param database DatabaseConnection instance for database operations
    # @return None
    def __init__(self, database: DatabaseConnection):
        self.database = database
