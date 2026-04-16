from sb_db_common import RepositoryBase
from sb_db_common.repo_context import RepositoryContext
from test_entity import TestEntity


class TestRepository(RepositoryBase):
    __table__ = TestEntity

RepositoryContext.register_repository(TestRepository)