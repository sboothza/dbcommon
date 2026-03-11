import datetime
import decimal
import re
from typing import Any

import oracledb

from .connection_base import ConnectionBase
from .mapped_field import Mapped


def _rewrite_returning_for_oracle(query: str) -> str:
    """Oracle requires RETURNING col INTO :var; rewrite PostgreSQL-style RETURNING col."""
    return re.sub(
        r"(\bRETURNING\s+\w+)\s*;?\s*$",
        r"\1 INTO :out_id",
        query.strip(),
        flags=re.IGNORECASE,
    )


class OracleConnection(ConnectionBase):
    field_type_maps = {
        int: "INT",
        float: "FLOAT",
        str: "VARCHAR({0})",
        datetime.datetime: "DATETIME",
        bool: "INT",
        decimal.Decimal: "DECIMAL({0},{1})"
    }

    property_type_maps = {
        bool: lambda x: x == 1
    }

    def __init__(self, connection_string: str = ""):
        # oracle://user:pass@localhost/db
        self.provider_name = "oracle"
        if connection_string == "":
            return
        super().__init__(connection_string)
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

    def escape_name(self, name:str)->str:
        return f"\"{name}\""

    def normalize_query(self, query: str) -> str:
        new_query = re.sub(r"select exists\((\w+)\);", "SELECT count(*) FROM user_tables WHERE table_name = '\\1';",
                           query, re.IGNORECASE)
        return new_query

    def generate_insert_query(self, table: type["TableBase"]) -> str:
        fields = [f for f in table.get_fields() if not f.auto_increment]
        field_parameters = [self.generate_parameter(f) for f in fields]
        query = f"INSERT INTO {table.__table_name__} ({", ".join([f.field_name for f in fields])}) VALUES ({", ".join(field_parameters)}) RETURNING {table._autoincrement_field.field_name};"
        return query

    def type_to_sql_type(self, field: Mapped) -> str:
        type_str: str = self.field_type_maps.get(field.field_type, "")
        if "{" in type_str:
            type_str = type_str.format(field.size, field.precision)
        return type_str

    def map_sql_value(self, sql_value, property_type: type) -> Any:
        map_func = self.property_type_maps.get(property_type, lambda x: x)
        return map_func(sql_value)

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
