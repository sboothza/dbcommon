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


def test_serializer_basic(dictionary_file, big_word_dictionary_file):
    naming = Naming(dictionary_file, big_word_dictionary_file)

    order: Order = Order(1, "Bill Jones", OrderStatus.PROCESSING)
    order.funny_bool_value = True
    order.order_lines.append(OrderLine(1, Product(1, "Soup"), 1))
    order.order_lines.append(OrderLine(2, Product(2, "Beans"), 1))
    order.order_lines.append(OrderLine(3, Product(3, "Milk"), 1))

    serializer = HardSerializer(naming=naming)
    json_str = serializer.serialize(order)
    print(json_str)
    order_dict = json.loads(json_str)

    new_order = serializer.de_serialize(json_str, Order)
    new_json_str = serializer.serialize(new_order)
    new_order_dict = json.loads(new_json_str)

    assert order_dict == new_order_dict
