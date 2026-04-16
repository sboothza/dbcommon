from complex_entity import ComplexEntity
from sb_db_common import RepositoryBase
from sb_db_common.repo_context import RepositoryContext


class ComplexRepository(RepositoryBase):
    __table__ = ComplexEntity

RepositoryContext.register_repository(ComplexRepository)