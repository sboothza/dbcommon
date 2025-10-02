import unittest

from src.sb_db_common import SessionFactory


class DbTests(unittest.TestCase):
    def setUp(self):
        SessionFactory.register()

    def test_crud_sqlite(self):
        with SessionFactory.connect("sqlite://:memory:") as session:
            session.execute("create table test(id integer not null primary key autoincrement, name text);")
            session.commit()
            # insert and select
            id = session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
            session.commit()
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            session.execute("update test set name = :name where id = :id", {"id": id, "name": "bob1"})
            session.commit()
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            session.execute("delete from test where id = :id", {"id": id})
            session.commit()
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertIsNone(row)

    def test_crud_mysql(self):
        with SessionFactory.connect("mysql://testuser:test@localhost/test") as session:
            session.execute("drop table test;")
            session.execute("create table test(id int not null primary key AUTO_INCREMENT, name varchar(50) null);")
            session.commit()
            # insert and select
            id = session.execute_lastrowid("insert into test(name) values (%(name)s);", {"name": "bob"})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            session.execute("update test set name = %(name)s where id = %(id)s", {"id": id, "name": "bob1"})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            session.execute("delete from test where id = %(id)s", {"id": id})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertIsNone(row)

    def test_crud_pgsql(self):
        with SessionFactory.connect("pgsql://testuser:test@localhost/test") as session:
            session.execute("drop table test;")
            session.commit()
            session.execute("create table test(id int not null primary key GENERATED ALWAYS AS IDENTITY, name varchar(50) null);")
            session.commit()
            # insert and select
            id = session.execute_lastrowid("insert into test(name) values (%(name)s) returning id;", {"name": "bob"})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            session.execute("update test set name = %(name)s where id = %(id)s", {"id": id, "name": "bob1"})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            session.execute("delete from test where id = %(id)s", {"id": id})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertIsNone(row)

    def test_mssql_integrated_security(self):
        with SessionFactory.connect("mssql://dummyuser:dummypass@TV4-POLSQLAG-01/UNSanctions?trusted_connection=yes") as session:
            rows = session.fetch("select * from [dbo].[questions]")
            for row in rows:
                print(row)
            self.assertTrue(True)


    def test_crud_mssql(self):
        with SessionFactory.connect("mssql://sa:E15ag0at123@localhost/test") as session:
            # session.execute("drop table test;")
            # session.commit()
            session.execute("create table test(id int identity(1,1) not null primary key, name varchar(50) null);")
            session.commit()
            # insert and select
            id = session.execute_lastrowid("insert into test(name) output inserted.id values (%(name)s);", {"name": "bob"})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob")

            # update
            session.execute("update test set name = %(name)s where id = %(id)s", {"id": id, "name": "bob1"})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertEqual(row[1], "bob1")

            # delete
            session.execute("delete from test where id = %(id)s", {"id": id})
            session.commit()
            row = session.fetch_one("select * from test where id = %(id)s", {"id": id})
            self.assertIsNone(row)

    def test_transactions(self):
        with SessionFactory.connect("sqlite://test.db") as session:
            try:
                session.execute("drop table test;")
            except:
                ...

            session.commit()
            session.execute("create table test(id integer not null primary key autoincrement, name text);")
            session.commit()

            id = session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob")

            session.rollback()
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertIsNone(row)

            id = session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            session.execute("update test set name = :name where id = :id", {"name": "Bill", "id": id})
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "Bill")
            session.commit()
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "Bill")

            session.execute("update test set name = :name where id = :id", {"name": "bob", "id": id})
            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "bob")
            session.rollback()

            row = session.fetch_one("select * from test where id = :id", {"id": id})
            self.assertEqual(row[1], "Bill")
