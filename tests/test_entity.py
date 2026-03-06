import datetime

from sb_db_common import TableBase
from sb_db_common.entity import entity
from sb_db_common.mapped_field import Mapped


@entity(table_name="testentity")
class TestEntity(TableBase):
    id = Mapped.mapped_column("id", "id", int, 0, primary_key=True, autoincrement=True)
    name = Mapped.mapped_column("name", "name", str, 1, 50, unique=True)
    address = Mapped.mapped_column("address", "address", str, 2, 200, unique=True)
    number_1 = Mapped.mapped_column("number_1", "number_1", int, 3)
    number_2 = Mapped.mapped_column("number_2", "number_2", float, 4)
    create_date = Mapped.mapped_column("create_date", "create_date", datetime.datetime, 5)
    active = Mapped.mapped_column("active", "active", bool, 6)
