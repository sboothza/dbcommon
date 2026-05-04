import re

import psycopg2

from . import PgSqlConnection
from . import ConnectionBase


class CockroachConnection(PgSqlConnection):
    def __init__(self, connection_string: str = ""):
        ConnectionBase.__init__(connection_string)

        self.provider_name = "cockroach"
        if connection_string == "":
            return

        match = re.match(r"cockroach://(\w+):(\w+)@(\w+)(:(\d+))?/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            if match.group(5):
                self.port = int(match.group(5))
            else:
                self.port = 26257
            self.database = match.group(6)

        else:
            raise Exception("Invalid connection string")

        self.connection = psycopg2.connect(user=self.user, password=self.password, host=self.hostname,
                                           database=self.database, port=self.port)
        self.cursor = self.connection.cursor()

    def start(self):
        ...
