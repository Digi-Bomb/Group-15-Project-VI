import os
import time
import mysql.connector


class DatabaseConnection:
    def __init__(self):
        self.host = "138.197.163.32"
        self.port = 3306
        self.user = "ezbooksserver"
        self.password = "BookEZDatabaseAccess0rz!"
        self.database = "BookEZDatabase"

    def connect(self):
        """Return a MySQL connection. Retries a few times before raising the last error."""
        last_error = None
        for i in range(5):
            try:
                test = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    ssl_disabled=True,
                )
                print("OOOOOOO WE ARE CONNECTED BABY!!!!")
                return test
            except mysql.connector.Error as exc:
                last_error = exc
                time.sleep(2)
        raise last_error


# def get_db():
#     """Return a MySQL connection. Retries a few times before raising the last error."""
#     last_error = None
#     for i in range(5):
#         try:
#             return mysql.connector.connect(
#                 host=os.environ.get("MYSQL_HOST", "localhost"),
#                 user=os.environ.get("MYSQL_USER"),
#                 password=os.environ.get("MYSQL_PASSWORD"),
#                 database=os.environ.get("MYSQL_DATABASE"),
#             )
#         except mysql.connector.Error as exc:
#             last_error = exc
#             time.sleep(2)
#     raise last_error
