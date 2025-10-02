import asyncio

from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor

class Session(object):
    def __init__(self, connection: ConnectionBase = None):
        self.connection = connection

    def __enter__(self):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.start())
        except RuntimeError:
            asyncio.run(self.start())
        return self

    def __exit__(self, type, value, traceback):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.close())
        except RuntimeError:
            asyncio.run(self.close())

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()

    async def close(self):
        if self.connection:
            await self.commit()
            await self.connection.close()

    async def start(self):
        await self.connection.start()

    async def commit(self):
        await self.connection.commit()
        await self.start()

    async def rollback(self):
        await self.connection.rollback()
        await self.start()

    async def execute(self, query: str, params=None) -> None:
        await self.connection.execute(query, params)

    async def execute_lastrowid(self, query: str, params=None):
        return await self.connection.execute_lastrowid(query, params)

    async def fetch_scalar(self, query: str, params=None):
        if params is None:
            params = {}
        row = await self.fetch_one(query, params)
        if row is not None:
            value = row[0]
        else:
            value = None
        return value

    async def fetch_one(self, query: str, params=None):
        if params is None:
            params = {}
        with ManagedCursor(self.connection.new_cursor()) as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchone()

    async def fetch(self, query: str, params=None) -> ManagedCursor:
        return await self.connection.fetch(query, params)

class PersistentSession(Session):
    __global_connection__: ConnectionBase = None

    def __init__(self, connection: ConnectionBase = None):
        #  super().__init__() # deliberately not calling this
        if PersistentSession.__global_connection__ is None:
            PersistentSession.__global_connection__ = connection

        self.connection = PersistentSession.__global_connection__
        # self.in_transaction = False
        # self.cursor = self.connection.cursor

    def __exit__(self, type, value, traceback):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.connection.commit())
        except RuntimeError:
            asyncio.run(self.connection.commit())

    async def close(self):
        pass
