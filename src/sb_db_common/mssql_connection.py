import datetime
import decimal
import re
from typing import Any

import pymssql

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .mapped_field import Mapped


class MsSqlConnection(ConnectionBase):
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
        # mssql://user:pass@localhost/db?trusted_connection=true&trust_cert=true
        self.provider_name = "mssql"
        if connection_string == "":
            return
        super().__init__(connection_string)
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

    def escape_name(self, name: str) -> str:
        return f"[{name}]"

    def normalize_query(self, query: str) -> str:
        new_query = re.sub(r":((\w)+)", "%(\\1)s", query)
        new_query = re.sub(r"select exists\((\w+)\);",
                           "SELECT count(*) FROM sys.tables WHERE name = '\\1' AND type = 'U';", new_query,
                           re.IGNORECASE)
        return new_query

    def generate_additional_create(self, table: type["TableBase"]) -> str:
        query = "declare @CurrentUser sysname; \r\n select @CurrentUser = user_name(); \r\n"
        table_comment = ""
        if table.__table_description__:
            table_comment += f"execute sp_addextendedproperty 'MS_Description', '{table.__table_description__}', 'user', @CurrentUser, 'table', '{table.__table_name__}';\r\n "

        column_descriptions = [
            f"execute sp_addextendedproperty 'MS_Description', '{f.description}', 'user', @CurrentUser, 'table', '{table.__table_name__}' , 'column', '{f.name}'; "
            for f in table.get_fields() if f.description != ""]
        query += table_comment
        query += ", \r\n".join(column_descriptions)
        return query

    def type_to_sql_type(self, field: Mapped) -> str:
        type_str: str = self.field_type_maps.get(field.field_type, "")
        if "{" in type_str:
            type_str = type_str.format(field.size, field.precision)
        return type_str

    def map_sql_value(self, sql_value, property_type: type) -> Any:
        map_func = self.property_type_maps.get(property_type, lambda x: x)
        return map_func(sql_value)

    def close(self):
        self.connection.close()
