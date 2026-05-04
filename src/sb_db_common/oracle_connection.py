import re

import oracledb

from .connection_base import ConnectionBase


def _rewrite_returning_for_oracle(query: str) -> str:
    """Oracle requires RETURNING col INTO :var; rewrite PostgreSQL-style RETURNING col."""
    return re.sub(
        r"(\bRETURNING\s+\w+)\s*;?\s*$",
        r"\1 INTO :out_id",
        query.strip(),
        flags=re.IGNORECASE,
    )


class OracleConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        # oracle://user:pass@localhost/db
        super().__init__(connection_string)

        self.provider_name = "oracle"
        if connection_string == "":
            return

        match = re.match(r"oracle://(\w+):(\w+)@(\w+)(:(\d+))?/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            if match.group(5):
                self.port = int(match.group(5))
            else:
                self.port = 1521
            self.database = match.group(6)
        else:
            raise Exception("Invalid connection string")

        self.connection = oracledb.connect(user=self.user, password=self.password, host=self.hostname,
                                           service_name=self.database, port=self.port)
        self.cursor = self.connection.cursor()

    def start(self):
        ...

    def _execute_lastrowid(self, query: str, params: dict):
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        # Oracle requires RETURNING col INTO :var; PostgreSQL uses RETURNING col and fetchone()
        if "RETURNING" in query.upper():
            query = _rewrite_returning_for_oracle(query)
            out_var = cursor.var(oracledb.NUMBER)
            params = {**params, "out_id": out_var}
            cursor.execute(query, params)
            return out_var.getvalue()[0]
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def close(self):
        self.connection.close()
