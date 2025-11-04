from pathlib import Path
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