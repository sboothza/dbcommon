from random import Random

from adaptors.adaptor_factory import AdaptorFactory
from base.database_objects import Database
from base.hard_serializer import HardSerializer
from base.naming import Naming, Name
from base.session_factory import SessionFactory
from person import Person, Gender


def main():
    definition = """
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

    naming = Naming("H:\\src\\sboothza\\dbcommon\\base\\dictionary.txt",
                    "H:\\src\\sboothza\\dbcommon\\base\\bigworddictionary.txt")

    # connection_string = "sqlite://H:\\src\\sboothza\\dbcommon\\person.db"
    # connection_string = "mysql://root:or9asm1c@localhost/person"
    connection_string = "pgsql://postgres:or9asm1c@localhost/person"
    adaptor = AdaptorFactory.get_adaptor_for_connection_string(connection_string, naming)
    database = adaptor.import_definition(definition, naming)
    print(database.name)
    json = adaptor.generate_schema_definition(database)
    print(json)

    table = database.get_table("person")

    random = Random()

    with SessionFactory.connect(connection_string) as session:
        insert_query = adaptor.generate_insert_script(table)

        for i in range(0, 100):
            father = Person(name="bob")
            father.make_parent(gender=Gender.MALE)
            father.insert(insert_query, session)
            mother = Person(name="bob")
            mother.make_parent(gender=Gender.FEMALE)
            mother.insert(insert_query, session)
            num_children = random.randint(0, 4)
            for j in range(0, num_children):
                child = Person(name="bob")
                child.make_child(father, mother)
                child.insert(insert_query, session)

    # find references and push in front
    # tables = adaptor.get_ordered_table_list(database)
    #
    # for table in tables:
    #     print(adaptor.generate_delete_script(table))
    #     print(adaptor.generate_drop_script(table))
    #     print(adaptor.generate_create_script(table))
    #     print(adaptor.generate_table_exists_script(table, "person"))
    #     print(adaptor.generate_count_script(table))
    #     print(adaptor.generate_insert_script(table))
    #     print(adaptor.generate_update_script(table))
    #     print(adaptor.generate_delete_script(table))
    #     print(adaptor.generate_fetch_by_id_script(table))
    #     print(adaptor.generate_item_exists_script(table))


if __name__ == '__main__':
    main()

