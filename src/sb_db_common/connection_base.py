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
        ...

    def commit(self):
        ...

    def rollback(self):
        ...

    def execute(self, query: str, params: None) -> ManagedCursor:
        ...

    def execute_lastrowid(self, query: str, params: dict):
        ...

    def fetch(self, query: str, params=None) -> ManagedCursor:
        ...

    def new_cursor(self) -> Any:
        return self.connection.cursor()

    def close(self):
        ...
