from typing import List

from base.database_objects import Database, KeyType, Table, FieldType
from base.hard_serializer import HardSerializer
from base.naming import Naming


class Adaptor(object):
    def __init__(self, connection: str, naming: Naming):
        self.connection = connection
        self.naming = naming
        self.serializer = HardSerializer(naming=self.naming)

    def import_schema(self, db_name: str) -> Database:
        pass

    def generate_schema_definition_file(self, database: Database, definition_file: str):
        with open(definition_file, 'w') as output_file:
            output_file.write(self.generate_schema_definition(database))
            output_file.flush()

    def generate_schema_definition(self, database: Database):
        return self.serializer.serialize(database, True)

    def import_definition_file(self, definition_file: str, naming: Naming) -> Database:
        text = ""
        with open(definition_file, 'r') as input_file:
            lines = input_file.readlines()
            for line in lines:
                text = text + line

        return self.import_definition(text, naming)

    def import_definition(self, definition: str, naming: Naming) -> Database:
        database = self.serializer.de_serialize(definition, Database)
        Adaptor._process_foreign_keys(database)
        return database

    @staticmethod
    def _process_foreign_keys(database: Database):
        for foreign_table in database.tables:
            for foreign_key in [key for key in foreign_table.keys if key.key_type == KeyType.ForeignKey]:
                primary_table = database.get_table(foreign_key.primary_table)
                primary_table.foreign_keys.append(foreign_key)

    @staticmethod
    def _add_dependant_tables(database: Database, table: Table, table_list: List[Table]):
        if table not in table_list:
            for fk in [key for key in table.keys if key.key_type == KeyType.ForeignKey]:
                primary_table = database.get_table(fk.primary_table)
                if primary_table == table:
                    if table not in table_list:
                        table_list.append(table)
                    return

                Adaptor._add_dependant_tables(database, primary_table, table_list)
            if table not in table_list:
                table_list.append(table)

    @staticmethod
    def get_ordered_table_list(database: Database) -> List[Table]:
        # find references and push in front
        tables: List[Table] = []
        for table in database.tables:
            Adaptor._add_dependant_tables(database, table, tables)

        return tables

    def escape_field_list(self, values: List[str]) -> List[str]:
        pass

    def generate_drop_script(self, table: Table) -> str:
        pass

    def generate_create_script(self, table: Table) -> str:
        pass

    def generate_table_exists_script(self, table: Table, db_name: str) -> str:
        pass

    def generate_count_script(self, table: Table) -> str:
        pass

    def generate_insert_script(self, table: Table) -> str:
        pass

    def generate_update_script(self, table: Table) -> str:
        pass

    def generate_delete_script(self, table: Table) -> str:
        pass

    def generate_fetch_by_id_script(self, table: Table) -> str:
        pass

    def generate_item_exists_script(self, table: Table) -> str:
        pass

    def get_field_type(self, field_type: FieldType) -> str:
        pass

    def must_remap_field(self, field_type: FieldType) -> tuple[bool, FieldType]:
        pass

    def replace_parameters(self, query: str) -> str:
        pass
