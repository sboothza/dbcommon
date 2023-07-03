from typing import List

from src.utilities.utils import pascal, get_fullname, find_first_in_array, find_first_in


class Name(object):
    def __init__(self, name: str = ""):
        self.name = name
        self.words: List[str] = []

    def raw(self, prefix: str = "", suffix: str = ""):
        return prefix + self.name + suffix

    def upper(self, prefix: str = "", suffix: str = ""):
        return (prefix + self.name + suffix).upper()

    def lower(self, prefix: str = "", suffix: str = ""):
        return (prefix + self.name + suffix).lower()

    def pascal(self, prefix: str = "", suffix: str = ""):
        result = "".join([pascal(word) for word in ([prefix] + self.words + [suffix]) if word != ""])
        return result

    def camel(self, prefix: str = "", suffix: str = ""):
        result = prefix + self.words[0].lower() + "".join(
            [pascal(word) for word in (self.words[1:] + [suffix]) if word != ""])
        return result

    def snake(self, prefix: str = "", suffix: str = ""):
        result = "_".join([word.lower() for word in ([prefix] + self.words + [suffix]) if word != ""])
        return result

    def upper_snake(self, prefix: str = "", suffix: str = ""):
        result = "_".join([word.upper() for word in ([prefix] + self.words + [suffix]) if word != ""])
        return result

    def __str__(self):
        return self.pascal()

    def map_to_dict(self, serializer):
        return self.name

    def map_to_object(self, obj, serializer, naming):
        self.name = obj


class Naming(object):
    def __init__(self, dictionary: str, big_dictionary: str):
        dictionary = get_fullname(dictionary)
        big_dictionary = get_fullname(big_dictionary)

        # normal words
        with open(dictionary, 'r') as dictionary_file:
            lines = dictionary_file.readlines()

        self.dictionary: List[str] = list()
        for line in lines:
            self.dictionary.append(line.replace("\n", ""))

        self.dictionary.sort(key=len, reverse=True)

        # big words
        with open(big_dictionary, 'r') as big_dictionary_file:
            lines = big_dictionary_file.readlines()

        self.big_dictionary: List[List[str]] = []

        for line in lines:
            line = line.replace("\n", "")
            words = line.split(",")
            words = [line.replace(",", "")] + words
            self.big_dictionary.append(words)

    def string_to_name(self, name: str) -> Name:
        value = name.strip().lower().replace("_", "").replace("-", "")
        found: list[str] = [""] * len(value)

        # big words
        pos, words = find_first_in_array(value, self.big_dictionary)
        while pos > -1:
            for i in range(len(words)):
                found[pos + i] = words[i]
                value = value.replace(words[i], " " * len(words[i]))

            pos, words = find_first_in_array(value, self.big_dictionary)

        # normal words
        while len(value.strip()) > 0:
            pos, word = find_first_in(value, self.dictionary)
            if pos > -1:
                found[pos] = word
                value = value.replace(word, " " * len(word))
            else:
                raise Exception(f"Not found {value}")

        result = Name(name)
        result.words = [w for w in found if w != ""]

        return result
