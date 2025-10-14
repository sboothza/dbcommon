import re

import psycopg2

from .exceptions import DataException
from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .utils import run_sync_as_async


class PgSqlConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        self.provider_name = "pgsql"
        if connection_string == "":
            return

        super().__init__(connection_string)
        match = re.match(r"pgsql:\/\/(\w+):(\w+)@(\w+)\/(\w+)", self.connection_string)
        if match:
            self.user = match.group(1)
            self.password = match.group(2)
            self.hostname = match.group(3)
            self.database = match.group(4)
        else:
            raise Exception("Invalid connection string")

        self.connection = psycopg2.connect(user=self.user, password=self.password, host=self.hostname,
                                           database=self.database)
        self.cursor = self.connection.cursor()

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

    @staticmethod
    def translate_datatypes(query: str) -> str:
        result = query
        result = re.sub(r"(TEXT)", "VARCHAR(MAX)", result, flags=re.IGNORECASE)
        result = re.sub(r"(REAL|FLOAT|DOUBLE)", "DOUBLE", result, flags=re.IGNORECASE)
        return result

    @staticmethod
    def translate_autoincrement(query: str) -> str:
        result = re.sub(r"(AUTOINCREMENT|AUTO_INCREMENT)", "GENERATED ALWAYS AS IDENTITY", query, flags=re.IGNORECASE)
        result = re.sub(r"(IDENTITY(1, 1))", "GENERATED ALWAYS AS IDENTITY", result, flags=re.IGNORECASE)
        return result

    @staticmethod
    def translate_parameters(query: str) -> str:
        result = query
        result = re.sub(r"(:(\w+))", "%(${2})s", query, flags=re.IGNORECASE)
        return result

    @staticmethod
    def translate_return_autoincrement_id(query:str)->str:
        result = query
        if "returning " in result.lower():
            return result

        match = re.match("output inserted\.(\w+)", result, flags=re.IGNORECASE)
        if match:
            field = match.group(1)
            result = result.replace(";", "")
            result = re.sub(r"output inserted\.(\w+)", "", result, flags=re.IGNORECASE)
            result += f" returning {field};"
            return result

        raise DataException("unknown return field!")

    def translate_query(self, query: str) -> str:
        # translate datatypes
        result = self.translate_datatypes(query)

        # translate AUTOINCREMENT
        result = self.translate_autoincrement(result)

        # translate parameters
        result = self.translate_parameters(result)

        # translate return AUTOINCREMENT id
        result = self.translate_return_autoincrement_id(result)
        return result