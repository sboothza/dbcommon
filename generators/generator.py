import os

from adaptors.adaptor import Adaptor
from database_objects import Database, Table, KeyType
from naming import Naming, Name
from serializer import serializer_instance
from source_writer import SourceWriter


class Generator(object):
    def __init__(self, naming: Naming):
        self.naming = naming

    def get_filename(self, name: Name, prefix: str = "", suffix: str = "") -> str:
        pass

    @staticmethod
    def import_definition(definition_file: str, naming: Naming) -> Database:
        return Adaptor.import_definition(definition_file, naming)

    def copy_templates(self, template_folder: str, output_folder: str):
        pass

    def generate_entities(self, database: Database, folder: str, adaptor: Adaptor, naming: Naming):
        if not os.path.exists(folder):
            os.makedirs(folder)
        for table in database.tables:
            self.generate_entity(table, database, os.path.join(folder, self.get_filename(table.name)),
                                 adaptor, naming)

    def generate_entity(self, table: Table, database: Database, filename: str, adaptor: Adaptor, naming: Naming):
        pass

    def generate_repositories(self, database: Database, folder: str, adaptor: Adaptor, naming: Naming):
        if not os.path.exists(folder):
            os.makedirs(folder)
        for table in database.tables:
            self.generate_repository(table, database,
                                     os.path.join(folder, self.get_filename(table.name, suffix="repository")),
                                     adaptor, naming)

    def generate_repository(self, table: Table, database: Database, filename: str, adaptor: Adaptor, naming: Naming):
        pass

    def generate_mapper(self, table: Table, writer: SourceWriter, adaptor: Adaptor):
        pass
