import re

from .connection_base import ConnectionBase
from .exceptions import DataException
from .mysql_connection import MySqlConnection
from .pgsql_connection import PgSqlConnection
from .session import Session, PersistentSession
from .sqlite_connection import SqliteConnection


class SessionFactory(object):
    @staticmethod
    def get_connection(connection_string: str) -> ConnectionBase:
        match = re.search(r"(\w+):\/\/(.+)", connection_string)
        if match:
            db_type = match.group(1)

            if db_type == "sqlite":
                return SqliteConnection(connection_string)
            elif db_type == "mysql":
                return MySqlConnection(connection_string)
            elif db_type == "pgsql":
                return PgSqlConnection(connection_string)
            else:
                raise DataException("invalid connection string")

    @staticmethod
    def connect(connection_string: str) -> Session:
        if "memory" in connection_string:
            if PersistentSession.__global_connection__ is None:
                session = PersistentSession(SessionFactory.get_connection(connection_string))
            else:
                session = PersistentSession()

        else:
            session = Session(SessionFactory.get_connection(connection_string))

        return session
