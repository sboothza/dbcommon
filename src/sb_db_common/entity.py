import inspect
import datetime
from typing import dataclass_transform, get_args, get_origin

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
                relation_symbols: dict[str, type] = {}
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

                        is_many_lookup = get_origin(field.field_type) is list or field.field_type is list or field.is_1_many
                        if is_many_lookup:
                            # handle 1 - n
                            if field.is_1_many:
                                rel_many = field.lookup_type
                            else:
                                rel_many_args = get_args(field.field_type)
                                if len(rel_many_args) == 0:
                                    raise TypeError(
                                        f"Lookup field {field.name!r} uses a list relationship "
                                        f"but does not declare an entity type."
                                    )
                                rel_many = rel_many_args[0]

                            rel_many_symbol = f"_rel_many_{field.name}"
                            relation_symbols[rel_many_symbol] = rel_many
                            ri_fk = row_index[fk_field.name]
                            fk_py = fk_field.field_type.__name__
                            txt += f"\t_fk_{field.name} = connection.map_sql_value(row[{ri_fk}], {fk_py})\r\n"
                            txt += f"\tif _fk_{field.name} is None:\r\n"
                            txt += f"\t\tsetattr(self, '{field.name}', [])\r\n"
                            txt += f"\telse:\r\n"
                            txt += f"\t\t_repo_{field.name} = context.get_repository({rel_many_symbol})\r\n"
                            txt += f"\t\tfrom sb_db_common.session_factory import SessionFactory\r\n"
                            txt += f"\t\twith SessionFactory.connect(connection.connection_string) as session:\r\n"
                            txt += f"\t\t\tobj_list = _repo_{field.name}.fetch_for_parent(session, _fk_{field.name})\r\n"
                            txt += f"\t\t\tsetattr(self, '{field.name}', obj_list)\r\n"
                        else:
                            # handle 1 - 1

                            rel_symbol = f"_rel_{field.name}"
                            relation_symbols[rel_symbol] = field.field_type
                            ri_fk = row_index[fk_field.name]
                            fk_py = fk_field.field_type.__name__
                            txt += f"\t_fk_{field.name} = connection.map_sql_value(row[{ri_fk}], {fk_py})\r\n"
                            txt += f"\tif _fk_{field.name} is None:\r\n"
                            txt += f"\t\tsetattr(self, '{field.name}', None)\r\n"
                            txt += f"\telse:\r\n"
                            txt += f"\t\t_proxy_cls_{field.name} = make_typed_entity_proxy({rel_symbol})\r\n"
                            txt += f"\t\tsetattr(self, '{field.name}', _proxy_cls_{field.name}(_fk_{field.name}, context, connection.connection_string))\r\n"
                    else:
                        ri = row_index[field.name]
                        txt += f"\tsetattr(self, '{field.name}', connection.map_sql_value(row[{ri}], {field.field_type.__name__}))\r\n"

                txt += f"\treturn self\r\n"
                txt += f"setattr(klass, 'map_row', map_row)"
                exec_ns = {**globals(), "klass": klass}
                exec_ns.update(relation_symbols)
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