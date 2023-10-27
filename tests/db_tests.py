import unittest

from src.sb_db_common import SessionFactory


class DbTests(unittest.TestCase):
    def setUp(self):
        pass

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