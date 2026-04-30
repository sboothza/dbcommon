import datetime
import decimal
import re
import sqlite3
from typing import Any

from .connection_base import ConnectionBase
from .mapped_field import Mapped, ReferenceType
from .utils import get_fullname, get_filename


class SqliteConnection(ConnectionBase):
    _sqlite_datetime_handlers_registered = False
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
        self._register_datetime_handlers()
        connection_string = self.connection_string.replace("sqlite://", "")
        connection_string = get_fullname(connection_string)
        self.connection = sqlite3.connect(connection_string, check_same_thread=False,
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.connection.isolation_level = None
        self.database = get_filename(connection_string)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")

    @classmethod
    def _register_datetime_handlers(cls):
        if cls._sqlite_datetime_handlers_registered:
            return
        sqlite3.register_adapter(datetime.datetime, cls._adapt_datetime)
        sqlite3.register_converter("TIMESTAMP", cls._convert_timestamp)
        cls._sqlite_datetime_handlers_registered = True

    @staticmethod
    def _adapt_datetime(value: datetime.datetime) -> str:
        return value.isoformat(sep=" ")

    @staticmethod
    def _convert_timestamp(value: bytes) -> datetime.datetime:
        value_str = value.decode()
        if value_str.endswith("Z"):
            value_str = f"{value_str[:-1]}+00:00"
        try:
            return datetime.datetime.fromisoformat(value_str)
        except ValueError:
            try:
                return datetime.datetime.strptime(value_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                return datetime.datetime.strptime(value_str, "%Y-%m-%d %H:%M:%S")

    def escape_name(self, name: str) -> str:
        return f"\"{name}\""

    def generate_field_definition(self, field: Mapped) -> str:
        return f"{self.escape_name(field.field_name)} {self.type_to_sql_type(field)} {self.generate_nullable(field)} {self.generate_is_pk(field)} {self.generate_autoincrement(field)}"

    def normalize_query(self, query: str) -> str:
        # "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='table_name';"
        new_query = re.sub(r"select exists\((\w+)\);",
                           "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='\\1';", query,
                           re.IGNORECASE)
        return new_query

    def generate_create_query(self, table: type["TableBase"]) -> str:
        fields:list[Mapped] = table.get_fields()
        field_defs = [self.generate_field_definition(f) for f in fields if f.reference_type == ReferenceType.NoReference]

        query = f"CREATE TABLE {self.escape_name(table.__table_name__)} \r\n"
        query += f"({',\r\n '.join(field_defs)}\r\n);\r\n"
        query += self.generate_create_indexes(table)
        query += self.generate_additional_create(table)
        return self.normalize_query(query)

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
