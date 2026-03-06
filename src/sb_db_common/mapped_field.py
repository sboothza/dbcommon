from __future__ import annotations


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

    def __str__(self):
        return self.name

    @staticmethod
    def mapped_column(name: str = None, field_name: str = None, field_type: type = int, order: int = 0, size: int = 50, precision: int = 2, primary_key: bool = False,
                      autoincrement: bool = False, unique: bool = False,
                      optional: bool = False,
                      default: str = "", ignore: bool = False) -> Mapped:

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

        return mapped
