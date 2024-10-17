import sqlite3
from typing import Any

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .utils import get_fullname, get_filename


class SqliteConnection(ConnectionBase):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        self.provider_name = "sqlite"
        connection_string = self.connection_string.replace("sqlite://", "")
        connection_string = get_fullname(connection_string)
        self.connection = sqlite3.connect(connection_string, check_same_thread=False)
        self.connection.isolation_level = None
        self.database = get_filename(connection_string)
        self.cursor = self.connection.cursor()

    def start(self):
        self.cursor.execute("BEGIN TRANSACTION;", {})

    def commit(self):
        self.cursor.execute("COMMIT;")

    def rollback(self):
        self.cursor.execute("ROLLBACK;")

    def execute(self, query: str, params: None):
        if params is None:
            params = {}
        self.cursor.execute(query, params)

    def execute_lastrowid(self, query: str, params: {})->Any:
        if params is None:
            params = {}
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def fetch(self, query: str, params=None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return ManagedCursor(cursor)

    def close(self):
        self.connection.close()
