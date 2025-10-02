import asyncio
import unittest

from src.sb_db_common import SessionFactory


class DbTests(unittest.TestCase):
    def setUp(self):
        SessionFactory.register()

    async def _test_crud_sqlite(self):
        async with SessionFactory.connect("sqlite://:memory:") as session:
            await session.execute("create table test(id integer not null primary key autoincrement, name text);")
            await session.commit()
            # insert and select
            id = await session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            await session.execute("update test set name = :name where id = :id", {"id": id, "name": "bob1"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            await session.execute("delete from test where id = :id", {"id": id})
            await session.commit()
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertIsNone(row)

    def test_crud_sqlite(self):
        asyncio.run(self._test_crud_sqlite())

    async def test_crud_mysql(self):
        with SessionFactory.connect("mysql://testuser:test@localhost/test") as session:
            await session.execute("drop table test;")
            await session.execute(
                "create table test(id int not null primary key AUTO_INCREMENT, name varchar(50) null);")
            await session.commit()
            # insert and select
            id = await session.execute_lastrowid("insert into test(name) values (%(name)s);", {"name": "bob"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            await session.execute("update test set name = %(name)s where id = %(id)s", {"id": id, "name": "bob1"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            await session.execute("delete from test where id = %(id)s", {"id": id})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertIsNone(row)

    async def test_crud_pgsql(self):
        with SessionFactory.connect("pgsql://testuser:test@localhost/test") as session:
            await session.execute("drop table test;")
            await session.commit()
            await session.execute(
                "create table test(id int not null primary key GENERATED ALWAYS AS IDENTITY, name varchar(50) null);")
            await session.commit()
            # insert and select
            id = await session.execute_lastrowid("insert into test(name) values (%(name)s) returning id;", {"name": "bob"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            await session.execute("update test set name = %(name)s where id = %(id)s", {"id": id, "name": "bob1"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            await session.execute("delete from test where id = %(id)s", {"id": id})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertIsNone(row)

    async def test_mssql_integrated_security(self):
        with SessionFactory.connect("mssql://dummyuser:dummypass@TV4-POLSQLAG-01/UNSanctions?trusted_connection=yes") as session:
            rows = await session.fetch("select * from [dbo].[questions]")
            for row in rows:
                print(row)
            self.assertTrue(True)


    async def test_crud_mssql(self):
        with SessionFactory.connect("mssql://sa:E15ag0at123@localhost/test") as session:
            # session.execute("drop table test;")
            # session.commit()
            await session.execute(
                "create table test(id int identity(1,1) not null primary key, name varchar(50) null);")
            await session.commit()
            # insert and select
            id = await session.execute_lastrowid("insert into test(name) output inserted.id values (%(name)s);", {"name": "bob"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            await session.execute("update test set name = %(name)s where id = %(id)s", {"id": id, "name": "bob1"})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            await session.execute("delete from test where id = %(id)s", {"id": id})
            await session.commit()
            row = await session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertIsNone(row)

    async def test_transactions(self):
        with SessionFactory.connect("sqlite://test.db") as session:
            try:
                await session.execute("drop table test;")
            except:
                ...

            await session.commit()
            await session.execute("create table test(id integer not null primary key autoincrement, name text);")
            await session.commit()

            id = await session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob")

            await session.rollback()
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertIsNone(row)

            id = await session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            await session.execute("update test set name = :name where id = :id", {"name": "Bill", "id": id})
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "Bill")
            await session.commit()
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "Bill")

            await session.execute("update test set name = :name where id = :id", {"name": "bob", "id": id})
            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob")
            await session.rollback()

            row = await session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "Bill")
