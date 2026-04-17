import inspect
import datetime
from typing import dataclass_transform

from . import Mapped
from .table_base import TableBase
from .entity_proxy import make_typed_entity_proxy

@dataclass_transform(field_specifiers=(Mapped.mapped_column,))
def entity(klass=None, table_name=None, description=None):
    def wrap(klass):

        def build_new_methods():
            if "__entity_built__" not in dir(klass):

                if not issubclass(klass, TableBase):
                    raise TypeError("Must be a subclass of TableBase")

                fields = klass.get_fields()

                txt = f"setattr(klass, '__table_name__', '{table_name}')\r\n"
                if description:
                    txt += f"setattr(klass, '__table_description__', '{description}')\r\n"
                exec(txt)

                # define_init(non_auto_fields)
                field_list = [
                    f"{f.name}=None"
                    for f in fields
                    if not f.auto_increment and not f.ignore and not f.is_lookup
                ]
                txt = f"def __init__(self, {', '.join(field_list)}):\r\n"
                for field in [f for f in fields if not f.auto_increment and not f.ignore and not f.is_lookup]:
                    txt += f"\tself.{field.name} = {field.name}\r\n"

                txt += "setattr(klass, '__init__', __init__)"
                exec(txt)

                # define __str__
                txt = f"def __str__(self):\r\n"
                field_list = [f"{{self.{f.name}}}" for f in fields if not f.ignore and not f.is_lookup]
                txt += f"\treturn f'{' '.join(field_list)}'\r\n"
                txt += "setattr(klass, '__str__', __str__)"
                exec(txt)

                # define_map_row(klass, fields) — row indices match SELECT of physical columns only (see connection_base)
                row_index: dict[str, int] = {}
                ri = 0
                for f in fields:
                    if f.ignore or f.is_lookup:
                        continue
                    row_index[f.name] = ri
                    ri += 1

                txt = "def map_row(self, context, row, connection) -> TableBase:\r\n"
                for field in fields:
                    if field.ignore:
                        continue
                    if field.is_lookup:
                        fk_field = next(
                            (
                                f
                                for f in fields
                                if not f.ignore and not f.is_lookup and f.field_name == field.field_name
                            ),
                            None,
                        )
                        if fk_field is None:
                            raise TypeError(
                                f"Lookup field {field.name!r} must pair with a non-lookup column "
                                f"having the same field_name (database column)."
                            )
                        ri_fk = row_index[fk_field.name]
                        fk_py = fk_field.field_type.__name__
                        rel = field.field_type.__name__
                        txt += f"\t_fk_{field.name} = connection.map_sql_value(row[{ri_fk}], {fk_py})\r\n"
                        txt += f"\tif _fk_{field.name} is None:\r\n"
                        txt += f"\t\tsetattr(self, '{field.name}', None)\r\n"
                        txt += f"\telse:\r\n"
                        txt += f"\t\t_proxy_cls_{field.name} = make_typed_entity_proxy({rel})\r\n"
                        txt += f"\t\tsetattr(self, '{field.name}', _proxy_cls_{field.name}(_fk_{field.name}, context, connection.connection_string))\r\n"
                    else:
                        ri = row_index[field.name]
                        txt += f"\tsetattr(self, '{field.name}', connection.map_sql_value(row[{ri}], {field.field_type.__name__}))\r\n"

                txt += f"\treturn self\r\n"
                txt += f"setattr(klass, 'map_row', map_row)"
                exec_ns = {**globals(), "klass": klass}
                for f in fields:
                    if f.is_lookup:
                        exec_ns[f.field_type.__name__] = f.field_type
                exec(txt, exec_ns)

                # get_insert_params(self)
                txt = "def get_insert_params(self) -> dict:\r\n"
                txt += "\treturn {"
                for i, field in enumerate([f for f in fields if not f.auto_increment]):
                    if not field.ignore and not field.is_lookup:
                        txt += f"\t\t\"{field.name}\": self.{field.name},\r\n"

                txt += "\t}\r\n"
                txt += f"setattr(klass, 'get_insert_params', get_insert_params)"
                exec(txt)

                # get_update_params(self)
                txt = "def get_update_params(self) -> dict:\r\n"
                txt += "\treturn {"
                for i, field in enumerate([f for f in fields]):
                    if not field.ignore and not field.is_lookup:
                        txt += f"\t\t\"{field.name}\": self.{field.name},\r\n"

                txt += "\t}\r\n"
                txt += f"setattr(klass, 'get_update_params', get_update_params)"
                exec(txt)

                # get_id_params(self)
                # txt = "def get_id_params(self) -> dict:\r\n"
                # txt += "\treturn {"
                # for i, field in enumerate([f for f in fields if f.primary_key]):
                #     if not field.ignore:
                #         txt += f"\t\t\"{field.name}\": self.{field.name},\r\n"
                #
                # txt += "\t}\r\n"
                # txt += f"setattr(klass, 'get_id_params', get_id_params)"
                # exec(txt)

                setattr(klass, "__entity_built__", True)

        build_new_methods()
        return klass

    if klass is None:
        return wrap
    return wrap(klass)