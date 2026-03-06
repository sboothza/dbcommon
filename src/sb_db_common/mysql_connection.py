import datetime
import decimal
import re
from typing import Any

import mysql.connector

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .mapped_field import Mapped


class MySqlConnection(ConnectionBase):
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
        self.provider_name = "mysql"
        if connection_string == "":
            return
        super().__init__(connection_string)

        match = re.match(r"mysql://(\w+):(\w+)@(\w+)(:(\d+))?/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            if match.group(5):
                self.port = int(match.group(5))
            else:
                self.port = 3306
            self.database = match.group(6)
        else:
            raise Exception("Invalid connection string")

        self.connection = mysql.connector.connect(user=self.user, password=self.password, host=self.hostname,
                                                  database=self.database, port=self.port)
        self.cursor = self.connection.cursor()

    def normalize_query(self, query: str) -> str:
        new_query = re.sub(r":((\w)+)", "%($1)s", query)
        new_query = re.sub(r"select exists\((\w+)\);",
                           "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = {0} AND TABLE_NAME = '$1';", new_query,
                           re.IGNORECASE)
        return new_query

    def type_to_sql_type(self, field: Mapped) -> str:
        type_str:str = self.field_type_maps.get(field.field_type, "")
        if "{" in type_str:
            type_str= type_str.format(field.size, field.precision)
        return type_str

    def map_sql_value(self, sql_value, property_type: type) -> Any:
        map_func = self.property_type_maps.get(property_type, lambda x: x)
        return map_func(sql_value)

    def _execute_lastrowid(self, query: str, params: dict) -> Any:
        if params is None:
            params = {}
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def close(self):
        self.connection.close()
