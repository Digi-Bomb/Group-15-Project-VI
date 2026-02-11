from database_connection import DatabaseConnection


class DatabaseReadingServices:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.conn = self.database.connect()
        self.cursor = self.conn.cursor()

    def get_specific_registered_user(self, username: str):
        result = self.cursor.execute(
            "SELECT RUID, username FROM RegisteredUser WHERE username = %s", (username,)
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No user found with that username."
