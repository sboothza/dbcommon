import re
import sqlite3
from typing import Any

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .utils import get_fullname, get_filename, run_sync_as_async

class SqliteConnection(ConnectionBase):
    def __init__(self, connection_string: str = ""):
        self.provider_name = "sqlite"
        if connection_string == "":
            return

        super().__init__(connection_string)
        connection_string = self.connection_string.replace("sqlite://", "")
        connection_string = get_fullname(connection_string)
        self.connection = sqlite3.connect(connection_string, check_same_thread=False)
        self.connection.isolation_level = None
        self.database = get_filename(connection_string)
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

    async def execute_lastrowid(self, query: str, params: None) -> Any:
        if params is None:
            params = {}

        def lam(cur):
            cur.execute(query, params)
            return cur.lastrowid

        return await run_sync_as_async(lam, self.cursor)

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
        result = re.sub(r"(varchar\((\w+)\))\w+", "TEXT", query, flags=re.IGNORECASE)
        result = re.sub(r"(char\((\w+)\))\w+", "TEXT", result, flags=re.IGNORECASE)
        result = re.sub(r"(BIGINT|SMALLINT|INT)\w+", "INTEGER", result, flags=re.IGNORECASE)
        result = re.sub(r"(REAL|FLOAT|DOUBLE)\w+", "REAL", result, flags=re.IGNORECASE)
        return result

    @staticmethod
    def translate_autoincrement(query: str) -> str:
        result = re.sub(r"(AUTOINCREMENT|AUTO_INCREMENT)", "AUTOINCREMENT", query, flags=re.IGNORECASE)
        result = re.sub(r"(GENERATED ALWAYS AS IDENTITY)", "AUTOINCREMENT", result, flags=re.IGNORECASE)
        result = re.sub(r"(IDENTITY(1, 1))", "AUTOINCREMENT", result, flags=re.IGNORECASE)
        return result

    @staticmethod
    def translate_return_autoincrement_id(query: str) -> str:
        result = query

        match = re.match(r"output inserted\.(\w+)", result, flags=re.IGNORECASE)
        if match:
            result = re.sub(r"output inserted\.(\w+)", "", result, flags=re.IGNORECASE)
            return result

        match = re.match(r"RETURNING (\w+)", result, flags=re.IGNORECASE)
        if match:
            result = re.sub(r"RETURNING (\w+)", "", result, flags=re.IGNORECASE)
            return result

        return result

    def translate_query(self, query: str) -> str:
        # translate datatypes
        result = self.translate_datatypes(query)

        # translate AUTOINCREMENT
        result = self.translate_autoincrement(result)

        # translate parameters
        # default params are fine

        # translate return AUTOINCREMENT id
        result = self.translate_return_autoincrement_id(result)
        return result
