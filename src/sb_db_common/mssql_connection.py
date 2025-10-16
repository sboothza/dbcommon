import re

import pymssql

from .exceptions import DataException
from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .utils import run_sync_as_async


class MsSqlConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        # mssql://user:pass@localhost/db?trusted_connection=true&trust_cert=true
        self.provider_name = "mssql"
        if connection_string == "":
            return
        super().__init__(connection_string)
        match = re.match(r"mssql:\/\/([^:]+)?:?([^@]+)?@([^\/]+)\/([^\?]+)(\?(.+))?", self.connection_string)
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

    async def start(self):
        await run_sync_as_async(self.cursor.execute, "BEGIN TRANSACTION;", {})

    async def commit(self):
        await run_sync_as_async(self.cursor.execute, "COMMIT;")

    async def rollback(self):
        await run_sync_as_async(self.cursor.execute, "ROLLBACK;")

    async def execute(self, query: str, params: None):
        if params is None:
            params = {}
        await run_sync_as_async(self.cursor.execute, query, params)

    async def execute_lastrowid(self, query: str, params: None):
        if params is None:
            params = {}
        cursor = self.connection.cursor()

        def lam(cur):
            cur.execute(query, params)
            return cur.fetchone()[0]

        return await run_sync_as_async(lam, cursor)

    async def fetch(self, query: str, params=None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()

        await run_sync_as_async(cursor.execute, query, params)
        return ManagedCursor(cursor)

    async def close(self):
        await run_sync_as_async(self.connection.close)

    # @staticmethod
    # def translate_datatypes(query: str) -> str:
    #     result = query
    #     result = re.sub(r"(TEXT)", "VARCHAR(MAX)", result, flags=re.IGNORECASE)
    #     result = re.sub(r"(INTEGER)", "INT", result, flags=re.IGNORECASE)
    #     result = re.sub(r"(REAL|FLOAT|DOUBLE)", "DOUBLE", result, flags=re.IGNORECASE)
    #     return result
    #
    # @staticmethod
    # def translate_autoincrement(query: str) -> str:
    #     result = re.sub(r"(\w+)\s+(INT|INTEGER)\s+(NOT\s+NULL)?\s+(PRIMARY\s+KEY)\s+(AUTOINCREMENT|AUTO_INCREMENT)", "${1} ${2} IDENTITY(1,1) ${3} ${4}", query, flags=re.IGNORECASE)
    #     result = re.sub(r"(\w+)\s+(INT|INTEGER)\s+(NOT\s+NULL)?\s+(PRIMARY\s+KEY)\s+(GENERATED ALWAYS AS IDENTITY)", "${1} ${2} IDENTITY(1,1) ${3} ${4}", result, flags=re.IGNORECASE)
    #     return result

    @staticmethod
    def translate_parameters(query: str) -> str:
        result = query
        result = re.sub(r"(:(\w+))", "%(\g<2>)s", result, flags=re.IGNORECASE)
        return result

    @staticmethod
    def translate_return_autoincrement_id(query: str) -> str:
        result = query

        if re.match("output inserted\.(\w+)", result, flags=re.IGNORECASE):
            return result

        if "returning" in result.lower():
            result = re.sub(r"(.+) VALUES (.+) RETURNING (\w+)", "${1} output inserted.${3} VALUES ${2}", result, flags=re.IGNORECASE)
            return result
        else:
            raise DataException("unknown return field!")

    def translate_query(self, query: str) -> str:
        # translate parameters
        result = self.translate_parameters(query)

        # translate return AUTOINCREMENT id
        result = self.translate_return_autoincrement_id(result)
        return result