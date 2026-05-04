import sqlite3
from typing import Any

from .connection_base import ConnectionBase
from .utils import get_fullname, get_filename


class SqliteConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        super().__init__(connection_string)

        self.provider_name = "sqlite"
        if connection_string == "":
            return

        connection_string = self.connection_string.replace("sqlite://", "")
        connection_string = get_fullname(connection_string)
        self.connection = sqlite3.connect(connection_string, check_same_thread=False,
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.connection.isolation_level = None
        self.database = get_filename(connection_string)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")

    def _execute_lastrowid(self, query: str, params: dict) -> Any:
        if params is None:
            params = {}
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def close(self):
        self.connection.close()
