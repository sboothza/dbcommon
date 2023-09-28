import json
from random import Random

import pytest

from adaptors.adaptor_factory import AdaptorFactory
from utilities.naming import Naming
from base.session_factory import SessionFactory
from person import Person, Gender


@pytest.fixture
def dictionary_file():
    return "../data/dictionary.txt"


@pytest.fixture
def big_word_dictionary_file():
    return "../data/bigworddictionary.txt"


@pytest.fixture
def schema():
    return """
        {"name":"test","tables":[{"name":"person","fields":[
        {"name":"id","type":"Integer","size":4,"auto_increment":true,"required":true},
        {"name":"father_id","type":"Integer","size":4},
        {"name":"mother_id","type":"Integer","size":4},
        {"name":"name","type":"String","size":50,"required":true},
        {"name":"gender","type":"String","size":1,"required":true},
        {"name":"address","type":"String","size":300},
        {"name":"creditcard","type":"String","size":20},
        {"name":"phone","type":"String","size":50},
        {"name":"email","type":"String","size":100},
        {"name":"dob","type":"Datetime"}],
        "pk":{"name":"PRIMARY","fields":["id"],"key_type":"PrimaryKey","referenced_table":"person"},"keys":[
        {"name":"person_father_FK","fields":["father_id"],"key_type":"ForeignKey","primary_table":"person",
        "primary_fields":["id"],"referenced_table":"person"},
        {"name":"person_mother_FK","fields":["mother_id"],"key_type":"ForeignKey","primary_table":"person",
        "primary_fields":["id"],"referenced_table":"person"}]}]}"""


@pytest.fixture
def sqlite_connection_string():
    return "sqlite://../person.db"


@pytest.fixture
def mysql_connection_string():
    return "mysql://root:or9asm1c@milleniumfalcon/person"


@pytest.fixture
def pgsql_connection_string():
    return "pgsql://postgres:or9asm1c@milleniumfalcon/person"


def test_serialize_deserialize(schema, dictionary_file, big_word_dictionary_file, sqlite_connection_string):
    definition = schema
    naming = Naming(dictionary_file, big_word_dictionary_file)

    connection_string = sqlite_connection_string
    adaptor = AdaptorFactory.get_adaptor_for_connection_string(connection_string, naming)
    database = adaptor.import_definition(definition, naming)
    table = database.get_table("person")

    assert table is not None
    assert len(table.fields) == 10
    assert table.pk is not None
    assert len(table.keys) == 2

    result = adaptor.generate_schema_definition(database)

    result_dict = json.loads(result)
    assert len(result_dict["tables"]) > 0 and result_dict["tables"][0] is not None
    result_table = result_dict["tables"][0]
    assert len(result_table["fields"]) == 10
    assert result_table["pk"] is not None
    assert len(result_table["keys"]) == 2


def generate_sql(schema, dictionary_file, big_word_dictionary_file, connection_string):
    definition = schema
    naming = Naming(dictionary_file, big_word_dictionary_file)

    adaptor = AdaptorFactory.get_adaptor_for_connection_string(connection_string, naming)
    database = adaptor.import_definition(definition, naming)
    table = database.get_table("person")
    result = {"delete": adaptor.generate_delete_script(table),
              "drop": adaptor.generate_drop_script(table),
              "create": adaptor.generate_create_script(table),
              "exists": adaptor.generate_table_exists_script(table),
              "count": adaptor.generate_count_script(table),
              "insert": adaptor.generate_insert_script(table),
              "update": adaptor.generate_update_script(table),
              "fetch": adaptor.generate_fetch_by_id_script(table),
              "item_exists": adaptor.generate_item_exists_script(table)}
    return result


def test_generate_sqlite(schema, dictionary_file, big_word_dictionary_file, sqlite_connection_string):
    sql = generate_sql(schema, dictionary_file, big_word_dictionary_file, sqlite_connection_string)
    assert sql["delete"] is not None
    assert sql["drop"] is not None
    assert sql["create"] is not None
    assert sql["exists"] is not None
    assert sql["count"] is not None
    assert sql["insert"] is not None
    assert sql["update"] is not None
    assert sql["fetch"] is not None
    assert sql["item_exists"] is not None
    print(sql["create"])

def test_generate_mysql(schema, dictionary_file, big_word_dictionary_file, mysql_connection_string):
    sql = generate_sql(schema, dictionary_file, big_word_dictionary_file, mysql_connection_string)
    assert sql["delete"] is not None
    assert sql["drop"] is not None
    assert sql["create"] is not None
    assert sql["exists"] is not None
    assert sql["count"] is not None
    assert sql["insert"] is not None
    assert sql["update"] is not None
    assert sql["fetch"] is not None
    assert sql["item_exists"] is not None
    print(sql["create"])


def test_generate_pgsql(schema, dictionary_file, big_word_dictionary_file, pgsql_connection_string):
    sql = generate_sql(schema, dictionary_file, big_word_dictionary_file, pgsql_connection_string)
    assert sql["delete"] is not None
    assert sql["drop"] is not None
    assert sql["create"] is not None
    assert sql["exists"] is not None
    assert sql["count"] is not None
    assert sql["insert"] is not None
    assert sql["update"] is not None
    assert sql["fetch"] is not None
    assert sql["item_exists"] is not None


def generate_data(schema, dictionary_file, big_word_dictionary_file, connection_string):
    definition = schema
    naming = Naming(dictionary_file, big_word_dictionary_file)

    adaptor = AdaptorFactory.get_adaptor_for_connection_string(connection_string, naming)
    database = adaptor.import_definition(definition, naming)
    table = database.get_table("person")

    people: [Person] = []
    random = Random()

    with SessionFactory.connect(connection_string) as session:
        table_exists_script = adaptor.generate_table_exists_script(table)
        if session.fetch_scalar(table_exists_script) is not None:
            drop_script = adaptor.generate_drop_script(table)
            session.execute(drop_script)
            session.commit()

        create_script = adaptor.generate_create_script(table)
        session.execute(create_script)
        session.commit()

        insert_query = adaptor.generate_insert_script(table)

        for i in range(0, 10):
            father = Person(name="bob")
            father.make_parent(gender=Gender.MALE)
            father.insert(insert_query, session)
            people.append(father)
            mother = Person(name="bob")
            mother.make_parent(gender=Gender.FEMALE)
            mother.insert(insert_query, session)
            people.append(mother)
            num_children = random.randint(0, 4)
            for j in range(0, num_children):
                child = Person(name="bob")
                child.make_child(father, mother)
                child.insert(insert_query, session)
                people.append(child)

        session.commit()

        # test
        get_sql = adaptor.generate_fetch_by_id_script(table)
        for person in people:
            row = session.fetch_one(get_sql, {"id": person.id})
            assert row is not None
            db_person = Person(name=" ")
            db_person.init_from_row(row)
            assert person == db_person


def test_generate_data_sqlite(schema, dictionary_file, big_word_dictionary_file, sqlite_connection_string):
    generate_data(schema, dictionary_file, big_word_dictionary_file, sqlite_connection_string)


def test_generate_data_mysql(schema, dictionary_file, big_word_dictionary_file, mysql_connection_string):
    generate_data(schema, dictionary_file, big_word_dictionary_file, mysql_connection_string)


def test_generate_data_pgsql(schema, dictionary_file, big_word_dictionary_file, pgsql_connection_string):
    generate_data(schema, dictionary_file, big_word_dictionary_file, pgsql_connection_string)
