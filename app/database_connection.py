import os
import time
import mysql.connector


class DatabaseConnection:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database


def get_db():
    """Return a MySQL connection. Retries a few times before raising the last error."""
    last_error = None
    for _ in range(5):
        try:
            return mysql.connector.connect(
                host=os.environ.get("MYSQL_HOST", "localhost"),
                user=os.environ.get("MYSQL_USER"),
                password=os.environ.get("MYSQL_PASSWORD"),
                database=os.environ.get("MYSQL_DATABASE"),
            )
        except mysql.connector.Error as exc:
            last_error = exc
            time.sleep(2)
    raise last_error
