from .managed_cursor import ManagedCursor


class ConnectionBase(object):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.database = ""

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def commit(self):
        pass

    def rollback(self):
        pass

    def execute(self, query: str, params: {}) -> ManagedCursor:
        pass

    def execute_lastrowid(self, query: str, params: {}):
        pass

    def close(self):
        pass


