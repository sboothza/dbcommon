import re

import mysql.connector

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor


class MySqlConnection(ConnectionBase):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        match = re.match(r"mysql:\/\/(\w+):(\w+)@(\w+)\/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            self.database = match.group(4)
        else:
            raise Exception("Invalid connection string")

        self.connection = mysql.connector.connect(user=self.user, password=self.password, host=self.hostname,
                                                  database=self.database)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def execute(self, query: str, params: None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query, params)
        return ManagedCursor(cursor)

    def execute_lastrowid(self, query: str, params: {}):
        if params is None:
            params = {}
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query, params)
        return cursor.lastrowid

    def close(self):
        self.commit()
        self.connection.close()
