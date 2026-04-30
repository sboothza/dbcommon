from pathlib import Path
import builtins
import importlib
from typing import List


def get_basename(path: str) -> str:
    p = Path(path)
    p.resolve()
    return p.name


def get_fullname(path: str) -> str:
    p = Path(path)
    p.resolve()
    return str(p.expanduser())


def get_filename(path: str) -> str:
    p = Path(path)
    p.resolve()
    return str(p.expanduser()).replace(str(p.parent), "").replace("/", "")


def split_clean(value: str, sep: str) -> List[str]:
    return list(filter(None, value.split(sep)))


def clean_string(dirty: str) -> str:
    while "\n" in dirty:
        dirty = dirty.replace("\n", " ")

    while "\r" in dirty:
        dirty = dirty.replace("\r", " ")

    while "\t" in dirty:
        dirty = dirty.replace("\t", " ")

    while "  " in dirty:
        dirty = dirty.replace("  ", " ")

    dirty = dirty.strip()
    if dirty[-1] == ",":
        dirty = dirty[:-1]
    return dirty.strip()


def find_in_list(value: str, items: list) -> int:
    for i in range(len(items)):
        if items[i] == value:
            return i
    return -1


def find_first_in(value: str, items: list[str]) -> tuple[int, str]:
    for i in range(len(items)):
        if items[i] in value:
            return value.find(items[i]), items[i]
    return -1, ""


def find_first_in_array(value: str, items: list[str]) -> tuple[int, list[str]]:
    for i in range(len(items)):
        if items[i][0] in value:
            return value.find(items[i][0]), items[i][1:]
    return -1, ""


def pascal(value: str) -> str:
    if value is None or value == "":
        return ""

    return value[0].upper() + value[1:].lower()


def safeget(d: dict, k, default):
    return d.get(k) if k in d else default


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