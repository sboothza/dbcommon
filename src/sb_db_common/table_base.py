from __future__ import annotations

import builtins
import importlib
import inspect

from . import DataException
from .connection_base import ConnectionBase
from .mapped_field import Mapped, Index, ReferenceType

def resolve_type(type_name: str) -> type:
    if type_name is None:
        raise ValueError("type_name cannot be None")

    name = type_name.strip()
    if name == "":
        raise ValueError("type_name cannot be empty")

    # Fast-path for common builtins.
    builtin_type = getattr(builtins, name, None)
    if isinstance(builtin_type, type):
        return builtin_type

    # Support fully qualified paths, e.g. datetime.datetime.
    if "." in name:
        module_name, attr_name = name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        resolved = getattr(module, attr_name)
        if isinstance(resolved, type):
            return resolved
        raise TypeError(f"{name!r} resolves to a non-type value")

    raise ValueError(
        f"Unknown type name: {type_name!r}. "
        f"Use a builtin type name (e.g. 'int') or a fully qualified path (e.g. 'datetime.datetime')."
    )

class TableBase:
    __table_name__ = ""
    __table_description__ = ""
    __table_created_at__ = ""
    __table_updated_at__ = ""
    __table_exists_script__ = ""
    __table_count_script__ = ""
    __create_script__ = ""
    __insert_script__ = ""
    __update_script__ = ""
    __delete_script__ = ""
    __drop_script__ = ""
    __fetch_by_id_script__ = ""
    __item_exists_script__ = ""
    __fetch_for_parent_script__ = ""

    _mapped_fields: dict[str, Mapped] = {}
    _mapped_field_list: list[Mapped] = []

    _autoincrement_field: Mapped = None
    _pk_field: Mapped = None

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
                        if attr.auto_increment:
                            if cls._autoincrement_field is None:
                                if attr.field_type is not int:
                                    raise DataException("Autoincrement field must be int")
                                cls._autoincrement_field = attr
                            else:
                                raise DataException(f"More than one autoincrement field is defined on {cls.__name__}")
                        if attr.primary_key:
                            if cls._pk_field is None:
                                if attr.field_type is not int:
                                    raise DataException("Primary key field must be int")
                                cls._pk_field = attr
                            else:
                                raise DataException(f"More than one primary key field is defined on {cls.__name__}")

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

    def __init__(self, connection:ConnectionBase=None):
        ...

    def map_row(self, row, connection: ConnectionBase) -> TableBase:
        ...

    def get_insert_params(self) -> dict:
        ...

    def get_update_params(self) -> dict:
        ...

    @classmethod
    def generate_queries(cls, connection: ConnectionBase):
        # map remote references
        remote_lookups = [f for f in cls.get_fields() if f.reference_type == ReferenceType.Lookup]
        for remote_lookup in remote_lookups:
            if type(remote_lookup.field_type).__name__ == "str":
                remote_lookup.field_type = resolve_type(remote_lookup.field_type)
            remote_entity: TableBase = remote_lookup.field_type
            remote_field: Mapped = getattr(remote_entity, remote_lookup.join_parent_field_name)
            remote_field.lookup_field_name = remote_lookup.field_name
            remote_field.lookup_type = remote_lookup.lookup_type

        cls.__table_exists_script__ = connection.generate_exists_query(cls)
        cls.__table_count_script__ = connection.generate_count_query(cls)
        cls.__create_script__ = connection.generate_create_query(cls)
        cls.__insert_script__ = connection.generate_insert_query(cls)
        cls.__update_script__ = connection.generate_update_query(cls)
        cls.__delete_script__ = connection.generate_delete_query(cls)
        cls.__drop_script__ = connection.generate_drop_query(cls)
        cls.__fetch_by_id_script__ = connection.generate_fetch_by_id_query(cls)
        cls.__item_exists_script__ = connection.generate_item_exists_query(cls)
        cls.__fetch_for_parent_script__ = connection.generate_fetch_for_parent_query(cls)
