import datetime
import unittest

from sb_db_common.repo_context import RepositoryContext
from test_entity import TestEntity
from sb_db_common import SessionFactory
from test_repository import TestRepository


class EntityTests(unittest.TestCase):
    def test_sqlite(self):
        self._test_basic("sqlite://:memory:")

    def test_pgsql(self):
        self._test_basic("pgsql://postgres:postgres@localhost/postgres")

    def _test_basic(self, connection_string):
        context = RepositoryContext()
        repo = context.get_repository(TestEntity)
        with SessionFactory.connect(connection_string) as session:
            repo.prepare(session)

            repo.create_schema(session)

            dt = datetime.datetime.now()
            entity:TestEntity = TestEntity("Stephen", "1 my street", 34, 12.56, dt,True)

            entity = repo.add(session, entity)

            assert entity.id == 1
            assert entity.name == "Stephen"
            assert entity.address == "1 my street"
            assert entity.number_1 == 34
            assert entity.number_2 == 12.56
            assert entity.create_date == dt
            assert entity.active == True

            entity = repo._get_by_id(session, entity.id)
            assert entity.id == 1
            assert entity.name == "Stephen"
            assert entity.address == "1 my street"
            assert entity.number_1 == 34
            assert entity.number_2 == 12.56
            assert entity.create_date == dt
            assert entity.active == True

            entity.name = "Stephen2"
            entity.active = False
            repo.update(session, entity)
            entity = repo._get_by_id(session, entity.id)
            assert entity.id == 1
            assert entity.name == "Stephen2"
            assert entity.address == "1 my street"
            assert entity.number_1 == 34
            assert entity.number_2 == 12.56
            assert entity.create_date == dt
            assert entity.active == False


