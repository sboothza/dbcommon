import re

import pymssql

from .connection_base import ConnectionBase


class MsSqlConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        # mssql://user:pass@localhost/db?trusted_connection=true&trust_cert=true
        super().__init__(connection_string)

        self.provider_name = "mssql"
        if connection_string == "":
            return

        match = re.match(r"mssql://([^:]+)?:?([^@]+)?@([^/:]+)(:(\d+))?/([^?]+)(\?(.+))?", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            self.database = match.group(4)
            if match.group(5):
                self.port = int(match.group(5))
            else:
                self.port = 1433
            self.options = {}
            key_value_pairs = match.group(8)
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

    def close(self):
        self.connection.close()
