import json
from enum import Enum


class HardSerializer(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        if "naming" in kwargs:
            self.naming = kwargs.pop('naming')
        super().__init__(*args, **kwargs)

    def serialize(self, obj, pretty: bool = False):
        d = self.map_to_dict(obj)
        return json.dumps(d, cls=HardSerializer, indent="\t" if pretty else None)

    def map_to_dict(self, obj):
        if isinstance(obj, list):
            new_list = []
            for item in obj:
                new_item = self.map_to_dict(item)
                new_list.append(new_item)
            return new_list

        if hasattr(obj, 'map_to_dict'):
            return obj.map_to_dict(self)

        if isinstance(obj, Enum):
            return str(obj).replace("{}.".format(type(obj).__name__), "")

        if not isinstance(obj, dict):
            if hasattr(obj, '__dict__'):
                d = {k: v for (k, v) in obj.__dict__.items() if not k.startswith("_")}
            else:
                return obj
        else:
            d = obj

        for child in d:
            d[child] = self.map_to_dict(d[child])
        return d

    def de_serialize(self, json_data, cls):
        dct = json.loads(json_data)
        obj = self.map_to_object(dct, cls)
        return obj

    def map_to_object(self, source_obj, cls):
        if type(source_obj) is list:
            new_list = []
            for item in source_obj:
                new_item = self.map_to_object(item, cls=cls)
                new_list.append(new_item)
            return new_list

        new_obj = cls()
        if hasattr(new_obj, 'map_to_object'):
            new_obj.map_to_object(source_obj, self, self.naming)
            return new_obj

        if not isinstance(source_obj, dict):
            if cls == type(None):
                return source_obj
            return cls(source_obj)

        type_hint = {}
        if hasattr(new_obj, 'get_type_hint'):
            type_hint = new_obj.get_type_hint()

        for key in new_obj.__dict__.keys():
            prop_cls = type(new_obj.__dict__[key])
            if type_hint.get(key):
                prop_cls = type_hint.get(key)
            value = source_obj.get(key, "")
            new_obj.__dict__[key] = self.map_to_object(value, prop_cls)

        return new_obj
