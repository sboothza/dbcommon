from enum import Enum
from typing import List, Union

from utilities.hard_serializer import HardSerializer, Ignore
from utilities.naming import Name, Naming


class Product:
    id: int
    name: Name

    def __init__(self, id=0, name=""):
        self.id: int = id
        self.name = Name(name)


class OrderLine:
    id: int
    product: Product
    quantity: int

    def __init__(self, id=0, product=None, quantity: int = 0):
        self.id = id
        self.product: Product = product
        self.quantity: int = quantity


class OrderStatus(Enum):
    PENDING = 1
    PROCESSING = 2
    COMPLETE = 3


class Order:
    id: int
    name: Name
    order_lines: List[OrderLine]
    order_status: OrderStatus
    funny_bool_value: Union[bool, Ignore]

    def __init__(self, id: int = 0, name: str = "", status: OrderStatus = OrderStatus.PENDING):
        self.id = id
        self.name = Name(name)
        self.order_lines: List[OrderLine] = []
        self.order_status = status
        self.funny_bool_value = False

    def map_to_dict(self, serializer: HardSerializer):
        target = serializer.map_to_dict(self, True)
        target["funny_bool_value"] = 1 if self.funny_bool_value else 2
        return target

    def map_to_object(self, source_obj, serializer: HardSerializer, naming: Naming):
        serializer.map_to_object(source_obj, type(self), True, self)
        self.funny_bool_value = True if source_obj["funny_bool_value"] == 1 else False
