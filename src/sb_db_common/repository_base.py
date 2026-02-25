from typing import Union

from . import Session, DataException

from table_base import TableBase


class RepositoryBase:
    __table__ = TableBase

    def drop_schema(self, session: Session):
        self._execute(session, self.__table__.__drop_script__)

    def schema_exists(self, session: Session):
        script = self.__table__.__table_exists_script__.format(database=session.connection.database)
        result = self._fetch_scalar(session, script)
        if result == 0:
            return False

        return True

    def create_schema(self, session: Session):
        script = list(filter(None, self.__table__.__create_script__.split(";")))
        for line in script:
            self._execute(session, line + ";")

    @staticmethod
    def _fetch_scalar(session: Session, query: str, parameters: Union[None, dict] = None):
        if parameters is None:
            parameters = {}
        return session.fetch_scalar(query, parameters)

    @staticmethod
    def _fetch_one(session: Session, query: str, parameters: Union[None, dict] = None):
        if parameters is None:
            parameters = {}
        return session.fetch_one(query, parameters)

    @staticmethod
    def _execute(session: Session, query: str, parameters: Union[None, dict] = None):
        try:
            if parameters is None:
                parameters = {}
            session.execute(query, parameters)
        except Exception as ex:
            print(ex)

    @staticmethod
    def _execute_lastrowid(session: Session, query: str, parameters: Union[None, dict] = None):
        try:
            if parameters is None:
                parameters = {}
            # cursor = session.fetch(query, parameters)
            # return cursor.fetchone()[0]     # pgsql needs a different identity handler
            return session.execute_lastrowid(query, parameters)
        except Exception as ex:
            print(ex)
            session.rollback()
            raise

    def _get_by_id(self, session: Session, id: Union[None, dict]):
        if id is None:
            raise DataException("id cannot be null")
        row = self._fetch_one(session, self.__table__.__fetch_by_id_script__, id)
        if row:
            return self.__table__().map_row(row)
        return None

    def _item_exists(self, session: Session, id: Union[None, dict]):
        if id is None:
            raise DataException("id cannot be null")
        cnt = self._fetch_scalar(session, self.__table__.__item_exists_script__, id)
        return cnt > 0

    def fetch_one(self, session: Session, query: str, parameters: Union[None, dict] = None) -> \
            Union[TableBase, TableBase, None]:
        try:
            if parameters is None:
                parameters = {}
            row = self._fetch_one(session, query, parameters)
            if row:
                return self.__table__().map_row(row)
            return None
        except Exception as ex:
            print(ex)

    def fetch(self, session: Session, query: str, parameters: Union[None, dict] = None):
        try:
            if parameters is None:
                parameters = {}
            with session.fetch(query, parameters) as cursor:
                return [self.__table__().map_row(row) for row in cursor]
        except Exception as ex:
            print(ex)

    def count(self, session: Session):
        script = self.__table__.__table_count_script__
        return self._fetch_scalar(session, script)

    def add(self, session: Session, item: TableBase):
        pass

    def update(self, session: Session, item: TableBase):
        self._execute(session, item.__update_script__, item.get_update_params())

    def _delete(self, session: Session, id: Union[None, dict]):
        if id is None:
            raise DataException("id cannot be null")
        self._execute(session, self.__table__.__delete_script__, id)
