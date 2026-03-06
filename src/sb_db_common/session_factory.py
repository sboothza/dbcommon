import inspect
import re
import sys

from .connection_base import ConnectionBase
from .exceptions import DataException
# from .mssql_connection import MsSqlConnection
# from .mysql_connection import MySqlConnection
# from .pgsql_connection import PgSqlConnection
from .session import Session, PersistentSession

# from .sqlite_connection import SqliteConnection


class SessionFactory(object):
    connections:dict[str, ConnectionBase] = {}

    @staticmethod
    def get_connection(connection_string: str) -> ConnectionBase:
        match = re.search(r"(\w+):\/\/(.+)", connection_string)
        if match:
            db_type = match.group(1)

            if db_type in SessionFactory.connections:
                return SessionFactory.connections[db_type](connection_string)
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

    @staticmethod
    def register():
        for module in list(sys.modules.items()):
            for name, obj in inspect.getmembers(module[1]):
                if inspect.isclass(obj) and issubclass(obj, ConnectionBase) and obj != ConnectionBase:
                    connection = obj()
                    type = connection.db_type()
                    if type != "":
                        if type not in SessionFactory.connections:
                            print(f"Registering connection type: {type}")
                            SessionFactory.connections[type] = obj


SessionFactory.register()