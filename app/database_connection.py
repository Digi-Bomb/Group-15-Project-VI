import os
import time
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from flask import has_request_context, g


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

        During a Flask request, the connection is registered for automatic cleanup
        at request teardown (returning it to the pool).
        """
        if DatabaseConnection._pool is not None:
            cnx = self.get_connection()
        else:
            # Legacy fallback (your original behavior)
            last_error = None
            for _ in range(5):
                try:
                    cnx = mysql.connector.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        ssl_verify_cert=False,
                        ssl_disabled=False,
                    )
                    break
                except mysql.connector.Error as exc:
                    last_error = exc
                    time.sleep(2)
            else:
                raise last_error

        # ---- NEW: request-scoped tracking so connections always get closed ----
        if has_request_context():
            conns = getattr(g, "_db_conns", None)
            if conns is None:
                g._db_conns = []
                conns = g._db_conns
            conns.append(cnx)

        return cnx
