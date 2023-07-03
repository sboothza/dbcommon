from typing import TextIO


class SourceWriter(object):
    __indent_level__ = 4

    def __init__(self, file: TextIO):
        self.file = file
        self.indent_prefix = ""

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.file.flush()
        self.file.close()

    def indent(self):
        self.indent_prefix = self.indent_prefix + (" " * self.__indent_level__)

    def unindent(self):
        self.indent_prefix = self.indent_prefix[:-self.__indent_level__]

    def get_current_indent(self):
        return self.indent_prefix

    def writeln(self, line: str = ""):
        self.file.write(self.indent_prefix)
        self.file.write(line)
        self.file.write("\n")

        print(self.indent_prefix + line)

    def writeln_absolute(self, prefix, line: str = ""):
        self.file.write(prefix)
        self.file.write(line)
        self.file.write("\n")

        print(prefix + line)

    def writeln_wrap(self, max_length: int, next_line_start: int, line: str):
        # temp_line = line
        # while len(line) > 0:
        raise Exception("A bit hard - not done yet - don't forget about keywords and wrapping strings - ")
