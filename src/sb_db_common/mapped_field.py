from __future__ import annotations

from enum import Enum


class ReferenceType(Enum):
    NoReference = 0
    Lookup = 1
    OneToMany = 2
    ManyToMany = 3
    OneToOne = 4


class Mapped:
    name: str
    field_name: str
    field_type: type
    order: int
    size: int
    precision: int
    primary_key: bool
    auto_increment: bool
    unique: bool
    optional: bool
    default: str
    ignore: bool
    indexed: bool
    description: str
    init: bool
    lookup_type: type
    join_parent_field_name: str
    join_table_name: str
    join_child_field_name: str
    reference_type: ReferenceType
    lookup_field_name: str
    lookup_type: type

    def __set_name__(self, owner, name):
        # name is the class attribute name, e.g. "id"
        if not self.name:
            self.name = name
        if not self.field_name:
            self.field_name = name

    def __str__(self):
        return f"{self.field_name} - {self.description}"

    @staticmethod
    def mapped_column(name: str = None, field_name: str = None, field_type: type = int, order: int = 0, size: int = 50,
                      precision: int = 2, primary_key: bool = False, autoincrement: bool = False, unique: bool = False,
                      optional: bool = False, default: str = "", ignore: bool = False, indexed: bool = False,
                      description: str = "", init: bool = True) -> Mapped:
        mapped = Mapped()
        mapped.name = name
        mapped.field_name = field_name
        mapped.primary_key = primary_key
        mapped.auto_increment = autoincrement
        mapped.field_type = field_type
        mapped.order = order
        mapped.size = size
        mapped.precision = precision
        mapped.unique = unique
        mapped.optional = optional
        mapped.default = default
        mapped.ignore = ignore
        mapped.indexed = indexed
        mapped.description = description
        mapped.init = init
        mapped.lookup_type = field_type
        mapped.reference_type = ReferenceType.NoReference

        return mapped

    @staticmethod
    def mapped_reference(name: str = None, field_name: str = None, field_type: type = int,
                         reference_type: ReferenceType = ReferenceType.NoReference,
                         join_parent_field_name: str = "id", join_table_name: str = None,
                         join_child_field_name: str = "id") -> Mapped:
        '''
        reference can be:
        lookup - just needs the field_name and lookup_type to determine
        1-many - the child has a parent_id, so need lookup_type and join_parent_field_name to build list
        many-many - uses join table, need lookup_type,  join_table_name, join_parent_field_name and join_child_field_name.  looks up all children in join table, and builds list of field_type for those children
        '''
        mapped = Mapped()
        mapped.name = name
        mapped.field_name = field_name
        mapped.field_type = field_type
        mapped.lookup_type = field_type
        mapped.reference_type = reference_type
        mapped.join_parent_field_name = join_parent_field_name
        mapped.join_table_name = join_table_name
        mapped.join_child_field_name = join_child_field_name
        mapped.primary_key = False
        mapped.auto_increment = False
        mapped.order = 0
        mapped.size = 0
        mapped.precision = 0
        mapped.unique = False
        mapped.optional = False
        mapped.default = ""
        mapped.ignore = False
        mapped.indexed = False
        mapped.description = ""
        mapped.init = False

        return mapped


class Index:
    name: str
    fields: list[str]
    unique: bool
    description: str

    def __str__(self):
        return self.name

    @staticmethod
    def map_index(name: str = None, fields: list[str] = None, autoincrement: bool = False, unique: bool = False,
                  description: str = "") -> Index:
        mapped = Index()
        mapped.name = name
        mapped.fields = fields
        mapped.auto_increment = autoincrement
        mapped.unique = unique
        mapped.description = description
        return mapped
