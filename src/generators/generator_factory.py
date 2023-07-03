from src.generators.generator import Generator
from src.generators.python_generator import PythonGenerator
from src.utilities.naming import Naming


class GeneratorFactory(object):
    @classmethod
    def get_generator(cls, language: str, naming: Naming) -> Generator:
        if language == "python":
            return PythonGenerator(naming)
