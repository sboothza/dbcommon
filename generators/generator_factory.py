from generators.generator import Generator
from generators.python_generator import PythonGenerator
from naming import Naming


class GeneratorFactory(object):
    @classmethod
    def get_generator(cls, language: str, naming: Naming) -> Generator:
        if language == "python":
            return PythonGenerator(naming)
