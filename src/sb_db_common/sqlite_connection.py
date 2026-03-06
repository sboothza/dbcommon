import datetime
import decimal
import re
import sqlite3
from typing import Any

from .connection_base import ConnectionBase
from .mapped_field import Mapped
from .utils import get_fullname, get_filename


class SqliteConnection(ConnectionBase):
    field_type_maps = {
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
        datetime.datetime: "TIMESTAMP",
        bool: "INTEGER",
        decimal.Decimal: "REAL"
    }
    property_type_maps = {
        bool: lambda x: x == 1,
        decimal.Decimal: lambda x: decimal.Decimal(x)
    }

    def __init__(self, connection_string: str = ""):
        self.provider_name = "sqlite"
        if connection_string == "":
            return

        super().__init__(connection_string)
        connection_string = self.connection_string.replace("sqlite://", "")
        connection_string = get_fullname(connection_string)
        self.connection = sqlite3.connect(connection_string, check_same_thread=False,
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.connection.isolation_level = None
        self.database = get_filename(connection_string)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")

    def normalize_query(self, query: str) -> str:
        # "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='table_name';"
        new_query = re.sub(r"select exists\((\w+)\);",
                           "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='$1';", query, re.IGNORECASE)
        return new_query

    def type_to_sql_type(self, field: Mapped) -> str:
        type_str = self.field_type_maps.get(field.field_type, "TEXT")
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
