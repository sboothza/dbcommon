import re

import psycopg2

from .connection_base import ConnectionBase


class PgSqlConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        super().__init__(connection_string)

        self.provider_name = "pgsql"
        if connection_string == "":
            return

        match = re.match(r"pgsql://(\w+):(\w+)@(\w+)(:(\d+))?/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            if match.group(5):
                self.port = int(match.group(5))
            else:
                self.port = 5432
            self.database = match.group(6)

        else:
            raise Exception("Invalid connection string")

        self.connection = psycopg2.connect(user=self.user, password=self.password, host=self.hostname,
                                           database=self.database, port=self.port)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()
