from typing import Any

from .managed_cursor import ManagedCursor


class ConnectionBase(object):
    def __init__(self, connection_string: str = ""):
        self.connection_string: str = connection_string
        self.database: str = ""
        self.connection: Any = None
        self.provider_name: str = ""
        self.cursor = None

    def db_type(self):
        return self.provider_name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def start(self):
        self.cursor.execute("BEGIN TRANSACTION;")

    def commit(self):
        self.cursor.execute("COMMIT;")

    def rollback(self):
        self.cursor.execute("ROLLBACK;")

    def execute(self, query: str, params: None):
        self._execute(query, params)

    def _execute(self, query: str, params: None | dict):
        if params is None:
            params = {}
        self.cursor.execute(query, params)

    def execute_lastrowid(self, query: str, params: dict):
        return self._execute_lastrowid(query, params)

    def _execute_lastrowid(self, query: str, params: dict):
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def fetch(self, query: str, params=None) -> ManagedCursor:
        return self._fetch(query, params)

    def _fetch(self, query: str, params=dict | None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return ManagedCursor(cursor)

    def new_cursor(self) -> Any:
        return self.connection.cursor()

    def close(self):
        ...
