import inspect
import datetime

from .table_base import TableBase


def entity(klass=None, table_name=None, description=None):
    def wrap(klass):

        def escape_string(text: str) -> str:
            return text.replace("\"", "\\\"")

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
                # if "__init__" not in dir(klass):
                field_list = [f"{f.name}=None" for f in fields if not f.auto_increment and not f.ignore]
                txt = f"def __init__(self, {', '.join(field_list)}):\r\n"
                for field in [f for f in fields if not f.auto_increment and not f.ignore]:
                    txt += f"\tself.{field.name} = {field.name}\r\n"

                txt += "setattr(klass, '__init__', __init__)"
                exec(txt)

                # define __str__
                # if "__str__" not in dir(klass):
                txt = f"def __str__(self):\r\n"
                field_list = [f"{{self.{f.name}}}" for f in fields if not f.ignore]
                txt += f"\treturn f'{' '.join(field_list)}'\r\n"
                txt += "setattr(klass, '__str__', __str__)"
                exec(txt)

                # define_map_row(klass, fields)
                txt = "def map_row(self, row, connection) -> TableBase:\r\n"
                for i, field in enumerate([f for f in fields]):
                    if not field.ignore:
                        txt += f"\tsetattr(self, '{field.name}', connection.map_sql_value(row[{i}], {field.field_type.__name__}))\r\n"

                txt += f"\treturn self\r\n"
                txt += f"setattr(klass, 'map_row', map_row)"
                exec(txt)

                # get_insert_params(self)
                txt = "def get_insert_params(self) -> dict:\r\n"
                txt += "\treturn {"
                for i, field in enumerate([f for f in fields if not f.auto_increment]):
                    if not field.ignore:
                        txt += f"\t\t\"{field.name}\": self.{field.name},\r\n"

                txt += "\t}\r\n"
                txt += f"setattr(klass, 'get_insert_params', get_insert_params)"
                exec(txt)

                # get_update_params(self)
                txt = "def get_update_params(self) -> dict:\r\n"
                txt += "\treturn {"
                for i, field in enumerate([f for f in fields]):
                    if not field.ignore:
                        txt += f"\t\t\"{field.name}\": self.{field.name},\r\n"

                txt += "\t}\r\n"
                txt += f"setattr(klass, 'get_update_params', get_update_params)"
                exec(txt)

                # get_id_params(self)
                txt = "def get_id_params(self) -> dict:\r\n"
                txt += "\treturn {"
                for i, field in enumerate([f for f in fields if f.primary_key]):
                    if not field.ignore:
                        txt += f"\t\t\"{field.name}\": self.{field.name},\r\n"

                txt += "\t}\r\n"
                txt += f"setattr(klass, 'get_id_params', get_id_params)"
                exec(txt)

                setattr(klass, "__entity_built__", True)

        build_new_methods()
        return klass

    if klass is None:
        return wrap
    return wrap(klass)