import json
from random import Random

import pytest

from adaptors.adaptor_factory import AdaptorFactory
from sample_entities import Order, OrderLine, Product, OrderStatus
from utilities.hard_serializer import HardSerializer
from utilities.naming import Naming
from base.session_factory import SessionFactory
from person import Person, Gender


@pytest.fixture
def dictionary_file():
    return "../data/dictionary.txt"


@pytest.fixture
def big_word_dictionary_file():
    return "../data/bigworddictionary.txt"


def test_naming_1(dictionary_file, big_word_dictionary_file):
    naming = Naming(dictionary_file, big_word_dictionary_file)
    n1 = naming.string_to_name("customerorders")
    assert n1.snake() == "customer_orders"
    n2 = naming.string_to_name("mynameisbill")
    assert n2.snake() == "my_name_is_bill"
    n3 = naming.string_to_name("financialtransactionsledger")
    assert n3.snake() == "financial_transactions_ledger"
