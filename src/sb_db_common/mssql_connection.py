import re

import pymssql

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor

class MsSqlConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        # mssql://user:pass@localhost/db?trusted_connection=true&trust_cert=true
        self.provider_name = "mssql"
        if connection_string == "":
            return
        super().__init__(connection_string)
        match = re.match(r"mssql://([^:]+)?:?([^@]+)?@([^/]+)/([^?]+)(\?(.+))?", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            self.database = match.group(4)
            self.options = {}
            key_value_pairs = match.group(6)
            if key_value_pairs:
                key_value_pairs = key_value_pairs.split("&")
                for pair in key_value_pairs:
                    key, value = pair.split("=")
                    self.options[key] = value
        else:
            raise Exception("Invalid connection string")

        if self._trusted_connection():
            self.connection = pymssql.connect(server=self.hostname, database=self.database)
        else:
            self.connection = pymssql.connect(user=self.user, password=self.password, server=self.hostname,
                                              database=self.database)
        self.cursor = self.connection.cursor()

    def _trusted_connection(self):
        return self.options.get("trusted_connection", "yes") == "yes"

    # def _trust_cert(self):
    #     return self.options.get("trust_cert", "yes") == "yes"

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

    def execute_lastrowid(self, query: str, params: {}):
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
