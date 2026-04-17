import datetime

from sb_db_common.mapped_field import Mapped
from sb_db_common.entity import entity
from sb_db_common import TableBase




@entity(table_name="testentity")
class TestEntity(TableBase):
    id: int = Mapped.mapped_column("id", "id", int, 0, primary_key=True, autoincrement=True, init=False)
    name: str = Mapped.mapped_column("name", "name", str, 1, 50, unique=True)
    address: str = Mapped.mapped_column("address", "address", str, 2, 200, unique=True)
    number_1: int = Mapped.mapped_column("number_1", "number_1", int, 3)
    number_2: float = Mapped.mapped_column("number_2", "number_2", float, 4)
    create_date: datetime.datetime = Mapped.mapped_column("create_date", "create_date", datetime.datetime, 5)
    active: bool = Mapped.mapped_column("active", "active", bool, 6)
