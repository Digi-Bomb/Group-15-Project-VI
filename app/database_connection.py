import os
import time
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool


class DatabaseConnection:
    # Shared pool across all DatabaseConnection instances.
    _pool: MySQLConnectionPool | None = None

    def __init__(self):
        self.host = "138.197.163.32"
        self.port = 3306
        self.user = "ezbooksserver"
        self.password = "BookEZDatabaseAccess0rz!"
        self.database = "BookEZDatabase"

        # Instance view of the shared pool (kept for compatibility/debugging)
        self.pool = DatabaseConnection._pool

    def init_pool(self, pool_size: int = 10):
        """Initialize the shared MySQL connection pool.

        Call this once at application startup.
        """
        if DatabaseConnection._pool is not None:
            self.pool = DatabaseConnection._pool
            return self.pool

        last_error = None
        for _ in range(5):
            try:
                DatabaseConnection._pool = MySQLConnectionPool(
                    pool_name="bookez_pool",
                    pool_size=pool_size,
                    pool_reset_session=True,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    ssl_verify_cert=False,
                    ssl_disabled=False,
                )
                self.pool = DatabaseConnection._pool
                return self.pool
            except mysql.connector.Error as exc:
                last_error = exc
                time.sleep(2)

        raise last_error

    def get_connection(self):
        """Borrow a connection from the pool."""
        if DatabaseConnection._pool is None:
            raise RuntimeError("DB pool not initialized. Call init_pool() at startup.")
        return DatabaseConnection._pool.get_connection()

    def connect(self):
        """Return a MySQL connection.

        If a pool is initialized, this borrows a connection from the pool.
        Otherwise, falls back to creating a direct connection (legacy behavior).
        """
        if DatabaseConnection._pool is not None:
            return self.get_connection()

        # Legacy fallback (your original behavior)
        last_error = None
        for _ in range(5):
            try:
                return mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    ssl_verify_cert=False,
                    ssl_disabled=False,
                )
            except mysql.connector.Error as exc:
                last_error = exc
                time.sleep(2)
        raise last_error