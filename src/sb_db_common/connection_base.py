from typing import Any
import asyncio
from .managed_cursor import ManagedCursor


class ConnectionBase(object):
    def __init__(self, connection_string: str = ""):
        self.connection_string: str = connection_string
        self.database: str = ""
        self.connection: Any = None
        self.provider_name: str = ""
        self.cursor = None

    def db_type(self):
        return self.provider_name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.close())
        except RuntimeError:
            asyncio.run(self.close())

    async def start(self):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...

    async def execute(self, query: str, params: None) -> ManagedCursor:
        ...

    async def execute_lastrowid(self, query: str, params: Any):
        ...

    async def fetch(self, query: str, params=None) -> ManagedCursor:
        ...

    def new_cursor(self) -> Any:
        return self.connection.cursor()

    async def close(self):
        ...
