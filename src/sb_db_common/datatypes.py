from __future__ import annotations

import re
from enum import Enum

from .exceptions import DataException

class DataType(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    TEXT = 4
    BOOLEAN = 5
    DATETIME = 6

    @staticmethod
    def from_string(value: str) -> DataType:
        if value.lower() == "int" or value.lower() == "integer":
            return DataType.INT
        elif value.lower() == "float" or value.lower() == "real" or value.lower() == "double":
            return DataType.FLOAT
        elif value.lower() == "string" or value.lower() == "char" or value.lower() == "varchar":
            return DataType.STRING
        elif value.lower() == "text":
            return DataType.TEXT
        elif value.lower() == "boolean" or value.lower() == "bool" or value.lower() == "bit":
            return DataType.BOOLEAN
        raise DataException("invalid data type")

class FieldType:
    def __init__(self, name: str, data_type: DataType, size: int, nullable:bool, default_value: str = None,
                 is_primary_key: bool = False, is_unique: bool = False, is_auto_increment: bool = False):
        self.name = name
        self.data_type = data_type
        self.size = size
        self.nullable = nullable
        self.default_value = default_value
        self.is_primary_key = is_primary_key
        self.is_unique = is_unique
        self.is_auto_increment = is_auto_increment

    @staticmethod
    def from_string(field_def: str) -> FieldType:
        data_type: DataType = DataType.STRING
        size: int = 0
        nullable: bool = False
        is_primary_key: bool = False
        autoincrement: bool = False
        unique: bool = False
        default_value: str = None

        result = field_def
        match = re.match(r"^(\w+)\s+([\w()]+)(.*)", result, flags=re.IGNORECASE)
        if match:
            name = match.group(1)
            type_def = match.group(2)
            remainder = match.group(3)

            if type_def.lower() == "varchar(max)":
                data_type = DataType.TEXT
            else:
                match = re.match(r"varchar\((\d+)\)|char\((\d+)\)", type_def, flags=re.IGNORECASE)
                if match:
                    size = int(match.group(1))
                    data_type = DataType.STRING

                else:
                    match = re.match(r"(BIGINT|SMALLINT|INT)\w+", result, flags=re.IGNORECASE)
                    if match:
                        data_type = DataType.INT

                    else:
                        match = re.match(r"(REAL|FLOAT|DOUBLE)\w+", result, flags=re.IGNORECASE)
                        if match:
                            data_type = DataType.FLOAT

                        else:
                            match = re.match(r"(DATETIME|DATE|TIMESTAMP|TIME)\w+", result, flags=re.IGNORECASE)
                            if match:
                                data_type = DataType.DATETIME

                            else:
                                match = re.match(r"(BOOLEAN|BOOL|BIT)\w+", result, flags=re.IGNORECASE)
                                if match:
                                    data_type = DataType.BOOLEAN

                                else:
                                    raise DataException("invalid data type")

            remainder = re.sub(r"AUTO_INCREMENT", "AUTOINCREMENT", remainder, flags=re.IGNORECASE)
            remainder = re.sub(r"GENERATED ALWAYS AS IDENTITY", "AUTOINCREMENT", remainder, flags=re.IGNORECASE)
            remainder = re.sub(r"(.*)(IDENTITY\(1,1\))([^,]+)", "${1}${3} AUTOINCREMENT", remainder,
                               flags=re.IGNORECASE)

            match = re.match(r"(null|not null)?\s*(primary key)?\s*(autoincrement)?\s*(unique)?\s*(default\((\w+)\))?",
                             remainder, flags=re.IGNORECASE)

            if match:
                if match.group(1).lower() == "null":
                    nullable = True
                else:
                    nullable = False

                if match.group(2):
                    is_primary_key = True

                if match.group(3):
                    autoincrement = True

                if match.group(4):
                    unique = True

                if match.group(5):
                    default_value = match.group(6)

                field_type: FieldType = FieldType(name, data_type, size, nullable, default_value, is_primary_key, unique,
                                                  autoincrement)
                return field_type

        raise DataException("invalid field definition")
