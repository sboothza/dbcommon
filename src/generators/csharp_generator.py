from adaptors.adaptor import Adaptor
from generators.generator import Generator
from metadata.database_objects import Table, Database
from utilities.naming import Naming, Name
from utilities.source_writer import SourceWriter


class CSharpGenerator(Generator):
    def __init__(self, naming: Naming):
        super().__init__(naming)

    def get_filename(self, name: Name, prefix: str = "", suffix: str = "") -> str:
        return name.pascal(prefix, suffix) + ".cs"

    def copy_templates(self, template_folder: str, output_folder: str):
        pass

    def generate_entity(self, table: Table, database: Database, filename: str, adaptor: Adaptor, naming: Naming):
        pass

    def generate_repository(self, table: Table, database: Database, filename: str, adaptor: Adaptor, naming: Naming):
        pass

    def generate_mapper(self, table: Table, writer: SourceWriter, adaptor: Adaptor):
        pass