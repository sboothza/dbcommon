import datetime
import unittest

from complex_entity import ComplexEntity
from sb_db_common import SessionFactory
from sb_db_common.entity_proxy import make_typed_entity_proxy
from sb_db_common.repo_context import RepositoryContext
from test_entity import TestEntity
from test_repository import TestRepository
from complex_repository import ComplexRepository


class TestLazy(unittest.TestCase):
    def setUp(self):
        ...

    def test_entity(self):
        conn_str = "sqlite://:memory:"
        id = 1
        context = RepositoryContext()
        repo = context.get_repository(TestEntity)
        self.assertIsNotNone(repo)
        with SessionFactory.connect(conn_str) as session:
            repo.create_schema(session)
            result = repo.add(session, TestEntity(name="test", address="address", number_1=1, number_2=2, create_date=datetime.datetime.now(), active=True))
            id = result.id

        TestProxy = make_typed_entity_proxy(TestEntity)
        test_proxy = TestProxy(id, context, "sqlite://:memory:")
        self.assertIsNotNone(test_proxy)
        self.assertEqual(test_proxy.name, "test")
        self.assertEqual(test_proxy.address, "address")
        self.assertEqual(test_proxy.number_1, 1)
        self.assertEqual(test_proxy.number_2, 2)

    def test_complex(self):
        conn_str = "sqlite://:memory:"
        context = RepositoryContext()
        simple_repo = context.get_repository(TestEntity)
        complex_repo = context.get_repository(ComplexEntity)
        id = 1

        with SessionFactory.connect(conn_str) as session:
            simple_repo.create_schema(session)
            complex_repo.create_schema(session)
            session.commit()

            test_entity = simple_repo.add(session, TestEntity(name="test", address="address", number_1=1, number_2=2, create_date=datetime.datetime.now(), active=True))
            complex_entity = complex_repo.add(session, ComplexEntity(name="comp", address="compaddress", number_1=1, number_2=2, simple_entity_id=test_entity.id, create_date=datetime.datetime.now(), active=True))
            id = complex_entity.id

        with SessionFactory.connect(conn_str) as session:
            complex_entity = complex_repo._get_by_id(session, id)
            self.assertIsNotNone(complex_entity)
            self.assertEqual(complex_entity.name, "comp")
            self.assertEqual(complex_entity.address, "compaddress")
            self.assertEqual(complex_entity.simple_entity.name, "test")