import asyncio

class ManagedCursor(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cursor.close()

    async def close(self):
        self.cursor.close()

    async def execute(self, sql: str, params: None):
        if params is None:
            params = {}

        return await asyncio.get_event_loop().run_in_executor(None, self.cursor.execute, sql, params)

    async def executemany(self, sql: str, seq_of_parameters):
        return await asyncio.get_event_loop().run_in_executor(None, self.cursor.executemany, sql, seq_of_parameters)

    async def fetchall(self):
        return await asyncio.get_event_loop().run_in_executor(None, lambda cursor: cursor.fetchall(), self.cursor)

    async def fetchone(self):
        return await asyncio.get_event_loop().run_in_executor(None, lambda cursor: cursor.fetchone(), self.cursor)

    def __iter__(self):
        return self.cursor.__iter__()

    def __next__(self):
        return self.cursor.__next__()

    @property
    def connection(self):
        return self.cursor.connection

    @property
    def description(self):
        return self.cursor.description

    # @property
    # def lastrowid(self):
    #     return self.cursor.lastrowid

    @property
    async def rowcount(self):
        return await asyncio.get_event_loop().run_in_executor(None, self.cursor.rowcount, None)
