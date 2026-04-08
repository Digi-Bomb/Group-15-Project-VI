"""!
@file database_connection.py
@brief MySQL connection management with optional pooling.

The DatabaseConnection class supports:
- Initializing a shared MySQLConnectionPool at application startup
- Borrowing pooled connections on demand
- Falling back to direct mysql.connector connections if pooling is unavailable
- Request-scoped tracking of connections via Flask's `g` for automatic teardown
"""

import os
import time
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from flask import has_request_context, g
import threading


class DatabaseConnection:
    """!
    @brief Provides MySQL connections (pooled when available).

    Usage patterns:
    - Call init_pool() once at startup (recommended).
    - Call connect() wherever a DB connection is needed.

    @warning Credentials are currently hard-coded for development/demo use.
             For production, use environment variables or a secrets manager.
    """

    # Shared pool across all DatabaseConnection instances.
    _pool: MySQLConnectionPool | None = None
    _lock = threading.Lock()
    _active_connections = 0

    def __init__(self):
        """!

        @brief Construct a DatabaseConnection configuration wrapper.



        The actual pool is shared across all instances via the class variable `_pool`.

        """
        self.host = os.environ.get("MYSQL_HOST", "planner_mysql")
        self.port = int(os.environ.get("MYSQL_PORT", 3306))
        self.user = os.environ.get("MYSQL_USER", "root")
        self.password = os.environ.get("MYSQL_PASSWORD", "")
        self.database = os.environ.get("MYSQL_DATABASE", "test")

        # Instance view of the shared pool (kept for compatibility/debugging)
        self.pool = DatabaseConnection._pool

    def init_pool(self, pool_size: int = 500):
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
        # print(f"[CONNECT] request")
        if has_request_context():
            # Return existing connection for this request if already created
            if hasattr(g, "_db_conns"):
                return g._db_conn

        # Create new connection
        if DatabaseConnection._pool is not None:
            with DatabaseConnection._lock:
                DatabaseConnection._active_connections += 1

            cnx = self.get_connection()
        else:
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

        # Store connection once per request
        if has_request_context():
            g._db_conn = cnx

            if not hasattr(g, "_db_conns"):
                g._db_conns = []
            g._db_conns.append(cnx)

        return cnx
