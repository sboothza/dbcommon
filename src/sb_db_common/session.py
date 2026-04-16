from .connection_base import ConnectionBase
from .managed_cursor import ManagedCursor


class Session(object):
    connection: ConnectionBase = None

    def __init__(self, connection: ConnectionBase = None):
        self.connection = connection

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.commit()
        self.connection.close()

    def start(self):
        self.connection.start()

    def commit(self):
        self.connection.commit()
        self.start()

    def rollback(self):
        self.connection.rollback()
        self.start()

    def execute(self, query: str, params=None) -> None:
        self.connection.execute(query, params)

    def execute_lastrowid(self, query: str, params=None):
        return self.connection.execute_lastrowid(query, params)

    # def execute_outside_transaction(self, query: str, params=None) -> None:
    #     if params is None:
    #         params = {}
    #     self.connection.commit()
    #     self.connection.cursor.close()
    #     self.connection.execute(query, params)
    #     self.connection.start()

    def fetch_scalar(self, query: str, params=None):
        if params is None:
            params = {}
        row = self.fetch_one(query, params)
        if row is not None:
            value = row[0]
        else:
            value = None
        return value

    def fetch_one(self, query: str, params=None):
        if params is None:
            params = {}
        cursor = self.connection.new_cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetch(self, query: str, params=None) -> ManagedCursor:
        return self.connection.fetch(query, params)


class PersistentSession(Session):
    _global_session: PersistentSession = None

    def __new__(cls, connection: ConnectionBase = None):
        if cls._global_session is None:
            cls._global_session = super(PersistentSession, cls).__new__(cls)
        return cls._global_session

    def __init__(self, connection: ConnectionBase = None):
        #  super().__init__() # deliberately not calling this

        if self.connection is None:
            self.connection = connection
            self.in_transaction = False

    def __enter__(self):
        if not self.in_transaction:
            self.start()
            self.in_transaction = True
        return self

    def __exit__(self, type, value, traceback):
        if self.in_transaction:
            self.connection.commit()
            self.in_transaction = False

    def close(self):
        pass
