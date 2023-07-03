import re

import psycopg2

from src.base.connection_base import ConnectionBase
from src.base.managed_cursor import ManagedCursor


class PgSqlConnection(ConnectionBase):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        match = re.match(r"pgsql:\/\/(\w+):(\w+)@(\w+)\/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            self.database = match.group(4)
        else:
            raise Exception("Invalid connection string")

        self.connection = psycopg2.connect(user=self.user, password=self.password, host=self.hostname,
                                           database=self.database)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def execute(self, query: str, params: None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return ManagedCursor(cursor)

    def execute_lastrowid(self, query: str, params: {}):
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def close(self):
        self.commit()
        self.connection.close()
