import mysql.connector
from mysql.connector import Error


class databaseConnection:

    host = None
    database = None
    user = None
    password = None
    connection = None
    port = None

    def connect():
        try:
            connection = mysql.connector.connect(
                port=3306,
                host="host.docker.internal",
                database="BookEZDatabase",
                user="root",
                password="BookEZAppConfig1987",  # This should NOT be hard coded in production code
            )
            if connection.is_connected():
                print(
                    f"Connected to MySQL as user '{connection.user}' "
                    f"on database '{connection.database}'"
                )
                return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None
