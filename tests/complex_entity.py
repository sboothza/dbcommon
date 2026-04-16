import datetime

from sb_db_common import entity, TableBase, Mapped
from test_entity import TestEntity


@entity(table_name="complexentity")
class ComplexEntity(TableBase):
    id = Mapped.mapped_column("id", "id", int, 0, primary_key=True, autoincrement=True)
    name = Mapped.mapped_column("name", "name", str, 1, 50, unique=True)
    address = Mapped.mapped_column("address", "address", str, 2, 200, unique=True)
    number_1 = Mapped.mapped_column("number_1", "number_1", int, 3)
    number_2 = Mapped.mapped_column("number_2", "number_2", float, 4)
    simple_entity_id = Mapped.mapped_column("simple_entity_id", "simple_entity_id", int, 5)
    simple_entity = Mapped.mapped_column("simple_entity", "simple_entity_id", TestEntity, 6, is_lookup=True)
    create_date = Mapped.mapped_column("create_date", "create_date", datetime.datetime, 7)
    active = Mapped.mapped_column("active", "active", bool, 8)