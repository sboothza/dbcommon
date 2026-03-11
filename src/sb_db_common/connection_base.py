from typing import TYPE_CHECKING, Any

from .managed_cursor import ManagedCursor

if TYPE_CHECKING:
    from .table_base import TableBase
from .mapped_field import Mapped


class ConnectionBase(object):
    def __init__(self, connection_string: str = ""):
        self.connection_string: str = connection_string
        self.database: str = ""
        self.connection: Any = None
        self.provider_name: str = ""
        self.cursor = None

    def db_type(self):
        return self.provider_name

    def normalize_query(self, query: str) -> str:
        """
        convert all queries from parameter name = :name to specific format
        and exists queries to specific format - exists queries should be select exists(<tablename>) -> expecting 1 or 0
        """
        return query

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def start(self):
        self.cursor.execute("BEGIN TRANSACTION;")

    def commit(self):
        self.cursor.execute("COMMIT;")

    def rollback(self):
        self.cursor.execute("ROLLBACK;")

    def execute(self, query: str, params: None):
        self._execute(self.normalize_query(query), params)

    def _execute(self, query: str, params: None):
        if params is None:
            params = {}
        self.cursor.execute(query, params)

    def execute_lastrowid(self, query: str, params: dict):
        return self._execute_lastrowid(self.normalize_query(query), params)

    def _execute_lastrowid(self, query: str, params: dict):
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def fetch(self, query: str, params=None) -> ManagedCursor:
        return self._fetch(self.normalize_query(query), params)

    def _fetch(self, query: str, params=None) -> ManagedCursor:
        if params is None:
            params = {}
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return ManagedCursor(cursor)

    def new_cursor(self) -> Any:
        return self.connection.cursor()

    def close(self):
        ...

    def escape_name(self, name:str)->str:
        return name

    def generate_field_definition(self, field:Mapped)->str:
        return f"{self.escape_name(field.field_name)} {self.type_to_sql_type(field)} {self.generate_nullable(field)} {self.generate_is_pk(field)} {self.generate_autoincrement(field)}"

    def generate_parameter(self, field:Mapped)->str:
        return f":{field.field_name}"

    def type_to_sql_type(self, field:Mapped) -> str:
        ...

    def map_sql_value(self, sql_value, property_type: type) -> Any:
        return sql_value

    def generate_nullable(self, field: Mapped)->str:
        return "NULL" if field.optional else "NOT NULL"

    def generate_is_pk(self, field: Mapped)->str:
        return "PRIMARY KEY" if field.primary_key else ""

    def generate_autoincrement(self, field: Mapped)->str:
        return "AUTOINCREMENT" if field.auto_increment else ""

    def generate_exists_query(self, table: type["TableBase"]) -> str:
        query = f"select exists({self.escape_name(table.__table_name__)});"
        return self.normalize_query(query)

    def generate_count_query(self, table: type["TableBase"]) -> str:
        query = f"select count(*) from {self.escape_name(table.__table_name__)};"
        return self.normalize_query(query)

    def generate_create_query(self, table: type["TableBase"]) -> str:
        fields = table.get_fields()
        field_defs = [self.generate_field_definition(f) for f in fields]
        query = f"CREATE TABLE {self.escape_name(table.__table_name__)} ({", ".join(field_defs)} );\r\n"
        query += self.generate_create_indexes(table)
        return self.normalize_query(query)

    def generate_create_indexes(self, table: type["TableBase"]) -> str:
        fields = table.get_fields()
        indexes = table.get_indexes()
        all_queries = ""
        # do single field indexes first
        for field in [f for f in fields if f.indexed or f.unique]:
            query = f"CREATE {'UNIQUE' if field.unique else ''} INDEX {self.escape_name(field.name)}_index ON {self.escape_name(table.__table_name__)} ({self.escape_name(field.field_name)});"
            all_queries += query + "\r\n"

        # do separate indexes
        for index in indexes:
            query = f"CREATE {'UNIQUE' if index.unique else ''} INDEX {self.escape_name(index.name)} ON {self.escape_name(table.__table_name__)} ({', '.join([self.escape_name(f) for f in index.fields])});"
            all_queries += query + "\r\n"

        return all_queries

    def generate_insert_query(self, table: type["TableBase"]) -> str:
        fields = [f for f in table.get_fields() if not f.auto_increment]
        field_parameters = [self.generate_parameter(f) for f in fields]
        query = f"INSERT INTO {table.__table_name__} ({", ".join([f.field_name for f in fields])}) VALUES ({", ".join(field_parameters)});"
        return query

    def generate_update_query(self, table: type["TableBase"]) -> str:
        pk_fields = [f for f in table.get_fields() if f.primary_key]
        non_pk_fields = [f for f in table.get_fields() if not f.primary_key and not f.auto_increment]
        non_pk_updates = [f"{f.field_name} = :{f.field_name}" for f in non_pk_fields]
        pk_keys = [f"{f.field_name} = :{f.field_name}" for f in pk_fields]
        query = f"UPDATE {table.__table_name__} SET {', '.join(non_pk_updates)} WHERE {', '.join(pk_keys)};"
        new_query = self.normalize_query(query)
        return new_query

    def generate_delete_query(self, table: type["TableBase"]) -> str:
        pk_fields = [f for f in table.get_fields() if f.primary_key]
        pk_keys = [f"{f.field_name} = :{f.field_name}" for f in pk_fields]
        query = f"DELETE FROM {table.__table_name__} WHERE {', '.join(pk_keys)};"
        new_query = self.normalize_query(query)
        return new_query

    def generate_drop_query(self, table: type["TableBase"]) -> str:
        query = f"DROP TABLE {table.__table_name__};"
        return query

    def generate_fetch_by_id_query(self, table: type["TableBase"]) -> str:
        fields = table.get_fields()
        field_names = [f.field_name for f in fields]
        pk_fields = [f for f in table.get_fields() if f.primary_key]
        pk_keys = [f"{f.field_name} = :{f.field_name}" for f in pk_fields]
        query = f"SELECT {', '.join(field_names)} FROM {table.__table_name__} WHERE {', '.join(pk_keys)};"
        new_query = self.normalize_query(query)
        return new_query

    def generate_item_exists_query(self, table: type["TableBase"]) -> str:
        pk_fields = [f for f in table.get_fields() if f.primary_key]
        pk_keys = [f"{f.field_name} = :{f.field_name}" for f in pk_fields]
        query = f"SELECT COUNT(*) FROM {table.__table_name__} WHERE {', '.join(pk_keys)};"
        new_query = self.normalize_query(query)
        return new_query

