import json
from enum import Enum
from typing import get_type_hints, get_args, List


class Ignore:
    ...


class HardSerializer(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        if "naming" in kwargs:
            self.naming = kwargs.pop('naming')
        super().__init__(*args, **kwargs)

    def serialize(self, obj, pretty: bool = False):
        d = self.map_to_dict(obj, False)
        return json.dumps(d, cls=HardSerializer, indent="\t" if pretty else None)

    def map_to_dict(self, obj, bypass: bool = False):
        if isinstance(obj, list):
            new_list = []
            for item in obj:
                new_item = self.map_to_dict(item)
                new_list.append(new_item)
            return new_list

        if not bypass and hasattr(obj, 'map_to_dict'):
            return obj.map_to_dict(self)

        if isinstance(obj, Enum):
            return str(obj).replace(f"{type(obj).__name__}.", "")

        if not isinstance(obj, dict):
            if hasattr(obj, '__dict__'):
                d = {}
                hints = get_type_hints(type(obj))
                for key in obj.__dict__.keys():
                    field_type = hints.get(key)
                    args = get_args(field_type)
                    if not key.startswith("_") and Ignore not in args:
                        d[key] = obj.__dict__[key]
            else:
                return obj
        else:
            d = obj

        for child in d:
            d[child] = self.map_to_dict(d[child], False)
        return d

    def de_serialize(self, json_data, cls):
        dct = json.loads(json_data)
        obj = self.map_to_object(dct, cls)
        return obj

    def map_to_object(self, source_obj, cls, bypass: bool = False, target_object=None):
        if type(source_obj) is list:
            new_list = []
            for item in source_obj:
                new_item = self.map_to_object(item, cls)
                new_list.append(new_item)
            return new_list

        if bypass:
            new_obj = target_object
        else:
            if issubclass(cls, Enum):
                new_obj = cls[source_obj]
            else:
                new_obj = cls()

        if not bypass and hasattr(new_obj, 'map_to_object'):
            new_obj.map_to_object(source_obj, self, self.naming)
            return new_obj

        if issubclass(cls, Enum):
            return new_obj

        if not isinstance(source_obj, dict):
            if cls == type(None):
                return source_obj
            try:
                return cls(source_obj)
            except Exception as ex:
                print(ex)
                return None

        return self.populate_object_from_dict(new_obj, source_obj)

    @staticmethod
    def get_type_of_field(cls):
        try:
            sub_classes = get_args(cls)
            if sub_classes == ():
                return cls, False
            ignore = Ignore in sub_classes
            return sub_classes[0], ignore
        except:
            pass

        return cls

    def populate_object_from_dict(self, new_obj, source_obj):
        type_hints = get_type_hints(type(new_obj))
        for key in source_obj.keys():
            prop_cls = type(new_obj.__dict__[key])
            if type_hints.get(key):
                prop_cls = type_hints.get(key)
            value = source_obj.get(key, "")
            field_type, ignore = HardSerializer.get_type_of_field(prop_cls)
            if not ignore:
                new_obj.__dict__[key] = self.map_to_object(value, field_type, False)
        return new_obj
