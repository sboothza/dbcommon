import sqlite3
from typing import Any
import asyncio

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor
from .utils import get_fullname, get_filename

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
        await asyncio.get_event_loop().run_in_executor(None, self.cursor.execute, "BEGIN TRANSACTION;", {})

    async def commit(self):
        await asyncio.get_event_loop().run_in_executor(None, self.cursor.execute, "COMMIT;")

    async def rollback(self):
        await asyncio.get_event_loop().run_in_executor(None, self.cursor.execute, "ROLLBACK;")

    async def execute(self, query: str, params: None):
        if params is None:
            params = {}
        await asyncio.get_event_loop().run_in_executor(None, self.cursor.execute, query, params)

    async def execute_lastrowid(self, query: str, params: None) -> Any:
        if params is None:
            params = {}

        def lam(cur):
            cur.execute(query, params)
            return cur.lastrowid

        return await asyncio.get_event_loop().run_in_executor(None, lam, self.cursor)

    async def fetch(self, query: str, params=None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()

        await asyncio.get_event_loop().run_in_executor(None, cursor.execute, query, params)
        return ManagedCursor(cursor)

    async def close(self):
        await asyncio.get_event_loop().run_in_executor(None, self.connection.close, None)
