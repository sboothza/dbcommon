from typing import Union

from . import Session, DataException

from . import TableBase
import datetime

from .repo_context import RepositoryContext


class RepositoryBase:
    __table__ = TableBase

    def __init__(self):
        ...

    def prepare(self, session: Session):
        if self.__table__ is not None and session.connection is not None and self.__table__.__table_exists_script__ == "":
            self.__table__.generate_queries(session.connection)

    def drop_schema(self, session: Session):
        self.prepare(session)
        self._execute(session, self.__table__.__drop_script__)

    def schema_exists(self, session: Session):
        self.prepare(session)
        script = self.__table__.__table_exists_script__.format(database=session.connection.database)
        result = self._fetch_scalar(session, script)
        if result == 0:
            return False

        return True

    def create_schema(self, session: Session):
        self.prepare(session)
        script = list(filter(None, self.__table__.__create_script__.split(";")))
        for line in script:
            self._execute(session, line + ";")
            session.commit()

    def _fetch_scalar(self, session: Session, query: str, parameters: Union[None, dict] = None):
        self.prepare(session)
        if parameters is None:
            parameters = {}
        return session.fetch_scalar(query, parameters)

    def _fetch_one(self, session: Session, query: str, parameters: Union[None, dict] = None):
        self.prepare(session)
        if parameters is None:
            parameters = {}
        return session.fetch_one(query, parameters)

    def _execute(self, session: Session, query: str, parameters: Union[None, dict] = None):
        self.prepare(session)
        try:
            if parameters is None:
                parameters = {}
            session.execute(query, parameters)
        except Exception as ex:
            print(ex)

    def _execute_lastrowid(self, session: Session, query: str, parameters: Union[None, dict] = None):
        self.prepare(session)
        try:
            if parameters is None:
                parameters = {}
            return session.execute_lastrowid(query, parameters)
        except Exception as ex:
            print(ex)
            session.rollback()
            raise

    def _get_by_id(self, session: Session, id: Union[None, int]):
        self.prepare(session)
        if id is None:
            raise DataException("id cannot be null")
        row = self._fetch_one(session, self.__table__.__fetch_by_id_script__, {self.__table__._pk_field.name: id})
        if row:
            return self.__table__(connection=session.connection).map_row(row, session.connection)
        return None

    def _item_exists(self, session: Session, id: Union[None, int]):
        self.prepare(session)
        if id is None:
            raise DataException("id cannot be null")
        cnt = self._fetch_scalar(session, self.__table__.__item_exists_script__, {self.__table__._pk_field.name: id})
        return cnt > 0

    def fetch_one(self, session: Session, query: str, parameters: Union[None, dict] = None) -> \
            Union[TableBase, TableBase, None]:
        self.prepare(session)
        try:
            if parameters is None:
                parameters = {}
            row = self._fetch_one(session, query, parameters)
            if row:
                obj = self.__table__(connection=session.connection)
                return obj.map_row(row, session.connection)
            return None
        except Exception as ex:
            print(ex)

    def fetch(self, session: Session, query: str, parameters: Union[None, dict] = None):
        self.prepare(session)
        try:
            if parameters is None:
                parameters = {}
            with session.fetch(query, parameters) as cursor:
                return [self.__table__(connection=session.connection).map_row(row, session.connection) for row in cursor]
        except Exception as ex:
            print(ex)

    def fetch_for_parent(self, session: Session, parent_id: int) -> list[TableBase]:
        self.prepare(session)
        try:
            with session.fetch(self.__table__.__fetch_for_parent_script__, {"parent_id": parent_id}) as cursor:
                return [self.__table__(connection=session.connection).map_row(row, session.connection) for row in cursor]
        except Exception as ex:
            print(ex)

    def fetch_id_for_parent(self, session: Session, parent_id: int) -> list[int]:
        self.prepare(session)
        try:
            with session.fetch(self.__table__.__fetch_for_parent_script__, {"parent_id": parent_id}) as cursor:
                return [row[0] for row in cursor]
        except Exception as ex:
            print(ex)

    def count(self, session: Session) -> int:
        self.prepare(session)
        script = self.__table__.__table_count_script__
        return self._fetch_scalar(session, script)

    def add(self, session: Session, item: TableBase) -> TableBase:
        self.prepare(session)
        script = type(self).__table__.__insert_script__
        auto_increment_field = type(self).__table__._autoincrement_field
        if auto_increment_field is not None:
            auto_value = self._execute_lastrowid(session, script, item.get_insert_params())
            # first auto value
            setattr(item, auto_increment_field.name, auto_value)
        else:
            self._execute(session, script, item.get_insert_params())

        return item

    def update(self, session: Session, item: TableBase):
        self.prepare(session)
        self._execute(session, item.__update_script__, item.get_update_params())

    def _delete(self, session: Session, id: Union[None, int]):
        self.prepare(session)
        if id is None:
            raise DataException("id cannot be null")
        self._execute(session, self.__table__.__delete_script__, {self.__table__._pk_field.name: id})
