import re

import psycopg2

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor

class PgSqlConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        self.provider_name = "pgsql"
        if connection_string == "":
            return

        super().__init__(connection_string)
        match = re.match(r"pgsql://(\w+):(\w+)@(\w+)/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            self.database = match.group(4)
        else:
            raise Exception("Invalid connection string")

        self.connection = psycopg2.connect(user=self.user, password=self.password, host=self.hostname,
                                           database=self.database)
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

    def execute_lastrowid(self, query: str, params: dict):
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def fetch(self, query: str, params=None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return ManagedCursor(cursor)

    def close(self):
        self.connection.close()
