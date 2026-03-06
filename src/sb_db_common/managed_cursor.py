class ManagedCursor(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cursor.close()

    def close(self):
        self.cursor.close()

    def execute(self, sql: str, params: None):
        if params is None:
            params = {}
        return self.cursor.execute(sql, params)

    def executemany(self, sql: str, seq_of_parameters):
        return self.cursor.executemany(sql, seq_of_parameters)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def __iter__(self):
        return self.cursor.__iter__()

    def __next__(self):
        next = self.cursor.__next__()
        return next

    @property
    def connection(self):
        return self.cursor.connection

    @property
    def description(self):
        return [c[0] for c in self.cursor.description]

    # @property
    # def lastrowid(self):
    #     return self.cursor.lastrowid

    @property
    def rowcount(self):
        return self.cursor.rowcount
