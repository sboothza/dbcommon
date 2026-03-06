from src.sb_db_common import RepositoryBase
from test_entity import TestEntity


class TestRepository(RepositoryBase):
    __table__ = TestEntity

