import sqlite3

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .utils import get_fullname, get_filename


class SqliteConnection(ConnectionBase):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        connection_string = self.connection_string.replace("sqlite://", "")
        connection_string = get_fullname(connection_string)
        self.connection = sqlite3.connect(connection_string, check_same_thread=False)
        self.database = get_filename(connection_string)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def execute(self, query: str, params: None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.execute(query, params)
        return ManagedCursor(cursor)

    def execute_lastrowid(self, query: str, params: {}):
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid

    def close(self):
        self.connection.close()
