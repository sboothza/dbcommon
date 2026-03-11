from __future__ import annotations

import inspect

from .connection_base import ConnectionBase
from .mapped_field import Mapped, Index
import datetime



class TableBase:
    __table_name__ = ""
    __table_exists_script__ = ""
    __table_count_script__ = ""
    __create_script__ = ""
    __insert_script__ = ""
    __update_script__ = ""
    __delete_script__ = ""
    __drop_script__ = ""
    __fetch_by_id_script__ = ""
    __item_exists_script__ = ""

    _mapped_fields: dict[str, Mapped] = {}
    _mapped_field_list: list[Mapped] = []

    _autoincrement_field: Mapped = None

    _mapped_indexes: dict[str, Index] = {}
    _mapped_index_list: list[Index] = []

    @classmethod
    def get_fields(cls) -> list[Mapped]:
        if len(cls._mapped_fields) == 0:
            entity_class_fields = {}
            for kls in cls.__mro__:
                for name, attr in inspect.getmembers(kls):
                    if "Mapped" in type(attr).__name__ and name not in entity_class_fields:
                        entity_class_fields[name] = attr
                        if attr.auto_increment and cls._autoincrement_field is None:
                            cls._autoincrement_field = attr

            cls._mapped_fields = entity_class_fields
            cls._mapped_field_list = list(entity_class_fields.values())
            cls._mapped_field_list.sort(key=lambda f: f.order)

        return cls._mapped_field_list

    @classmethod
    def get_indexes(cls) -> list[Index]:
        if len(cls._mapped_indexes) == 0:
            entity_class_indexes = {}
            for kls in cls.__mro__:
                for name, attr in inspect.getmembers(kls):
                    if "Index" in type(attr).__name__ and name not in entity_class_indexes:
                        entity_class_indexes[name] = attr

            cls._mapped_indexes = entity_class_indexes
            cls._mapped_index_list = list(entity_class_indexes.values())

        return cls._mapped_index_list

    def map_row(self, row, connection: ConnectionBase) -> TableBase:
        ...

    def get_insert_params(self) -> dict:
        ...

    def get_update_params(self) -> dict:
        ...

    def get_id_params(self) -> dict:
        ...

    @classmethod
    def generate_queries(cls, connection: ConnectionBase):
        cls.__table_exists_script__ = connection.generate_exists_query(cls)
        cls.__table_count_script__ = connection.generate_count_query(cls)
        cls.__create_script__ = connection.generate_create_query(cls)
        cls.__insert_script__ = connection.generate_insert_query(cls)
        cls.__update_script__ = connection.generate_update_query(cls)
        cls.__delete_script__ = connection.generate_delete_query(cls)
        cls.__drop_script__ = connection.generate_drop_query(cls)
        cls.__fetch_by_id_script__ = connection.generate_fetch_by_id_query(cls)
        cls.__item_exists_script__ = connection.generate_item_exists_query(cls)
