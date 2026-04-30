from __future__ import annotations

import datetime
from enum import Enum

from sb_db_common import TableBase, Mapped, ConnectionBase, SessionFactory
from sb_db_common.entity_proxy import make_typed_entity_proxy
from sb_db_common.mapped_field import ReferenceType
from sb_db_common.repo_context import RepositoryContext


class InvoiceStatus(Enum):
    Initial = 0
    Pending = 1
    Completed = 2
    Canceled = 3


class Product(TableBase):
    __table_name__ = "product"
    id: int = Mapped.mapped_column(field_type=int, order=1, primary_key=True, autoincrement=True)
    name: str = Mapped.mapped_column(field_name="name", field_type=str, order=2)
    description: str = Mapped.mapped_column(field_name="description", field_type=str, order=3)
    quantity: float = Mapped.mapped_column(field_name="quantity", field_type=float, order=4)
    price: float = Mapped.mapped_column(field_name="price", field_type=float, order=5)

    def __init__(self, name: str = "", description: str = "", quantity: float = 0, price: float = 0, connection=None):
        self.name = name
        self.description = description
        self.quantity = quantity
        self.price = price

    def map_row(self, row, connection) -> TableBase:
        setattr(self, 'id', connection.map_sql_value(row[0], int))
        setattr(self, 'name', connection.map_sql_value(row[1], str))
        setattr(self, 'description', connection.map_sql_value(row[2], str))
        setattr(self, 'quantity', connection.map_sql_value(row[3], float))
        setattr(self, 'price', connection.map_sql_value(row[4], float))

        return self

    def get_insert_params(self) -> dict:
        return {"name": self.name, "description": self.description, "quantity": self.quantity, "price": self.price}

    def get_update_params(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description, "quantity": self.quantity,
                "price": self.price}


class InvoiceLine(TableBase):
    __table_name__ = "invoiceline"

    id: int = Mapped.mapped_column(field_type=int, order=1, primary_key=True, autoincrement=True)
    parent_id: int = Mapped.mapped_column(field_name="invoiceid", field_type=int, order=2, indexed=True)
    create_date: datetime.datetime = Mapped.mapped_column(field_name="createdate", field_type=datetime.datetime,
                                                          order=3)
    product_id: int = Mapped.mapped_column(field_name="productid", field_type=int, order=4)
    product: Product = Mapped.mapped_reference(field_name="productid", field_type=Product,
                                               reference_type=ReferenceType.Lookup)
    quantity: float = Mapped.mapped_column(field_type=float, order=5)
    invoice: Invoice = Mapped.mapped_reference(field_name="invoiceid", field_type="tests.parent_child.Invoice",
                                               reference_type=ReferenceType.Lookup)

    def __init__(self, parent_id: int = 0, create_date: datetime.datetime = datetime.datetime.now(),
                 product_id: int = 0, quantity: float = 0, connection=None):
        self.parent_id = parent_id
        self.create_date = create_date
        self.product_id = product_id
        if product_id is None:
            self.product = None
        else:
            _proxy_cls_product = make_typed_entity_proxy(Product)
            self.product = _proxy_cls_product(product_id, connection.connection_string)

        self.quantity = quantity
        if parent_id is None:
            self.invoice = None
        else:
            _proxy_cls_invoice = make_typed_entity_proxy(Invoice)
            self.invoice = _proxy_cls_invoice(parent_id, connection.connection_string)

    def map_row(self, row, connection) -> TableBase:
        setattr(self, 'id', connection.map_sql_value(row[0], int))
        setattr(self, 'parent_id', connection.map_sql_value(row[1], int))
        setattr(self, 'create_date', connection.map_sql_value(row[2], datetime.datetime))
        setattr(self, 'product_id', connection.map_sql_value(row[3], int))
        product_id = connection.map_sql_value(row[3], int)
        if product_id is None:
            setattr(self, 'product', None)
        else:
            _proxy_cls_product = make_typed_entity_proxy(Product)
            setattr(self, 'product', _proxy_cls_product(product_id, connection.connection_string))

        setattr(self, 'quantity', connection.map_sql_value(row[4], float))
        parent_id = connection.map_sql_value(row[3], int)
        if parent_id is None:
            setattr(self, 'invoice', None)
        else:
            _proxy_cls_invoice = make_typed_entity_proxy(Invoice)
            setattr(self, 'invoice', _proxy_cls_invoice(parent_id, connection.connection_string))

        return self

    def get_insert_params(self) -> dict:
        return {"invoiceid": self.parent_id, "createdate": self.create_date, "productid": self.product_id,
                "quantity": self.quantity}

    def get_update_params(self) -> dict:
        return {"id": self.id, "invoiceid": self.parent_id, "createdate": self.create_date,
                "productid": self.product_id, "quantity": self.quantity}


class Customer(TableBase):
    __table_name__ = "customer"

    id: int = Mapped.mapped_column(field_type=int, order=1, primary_key=True, autoincrement=True)
    name: str = Mapped.mapped_column(field_name="name", field_type=str, order=2)
    email: str = Mapped.mapped_column(field_name="email", field_type=str, order=3)
    phone: str = Mapped.mapped_column(field_name="phone", field_type=str, order=4)
    address: str = Mapped.mapped_column(field_name="address", field_type=str, order=5)

    def __init__(self, name: str = "", email: str = "", phone: str = "", address: str = "", connection=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

    def map_row(self, row, connection: ConnectionBase) -> TableBase:
        setattr(self, 'id', connection.map_sql_value(row[0], int))
        setattr(self, 'name', connection.map_sql_value(row[1], str))
        setattr(self, 'email', connection.map_sql_value(row[2], str))
        setattr(self, 'phone', connection.map_sql_value(row[3], str))
        setattr(self, 'address', connection.map_sql_value(row[4], str))

        return self

    def get_insert_params(self) -> dict:
        return {"name": self.name, "email": self.email, "phone": self.phone, "address": self.address}

    def get_update_params(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email, "phone": self.phone, "address": self.address}


class Invoice(TableBase):
    __table_name__ = "invoice"

    id = Mapped.mapped_column(field_type=int, order=1, primary_key=True, autoincrement=True)
    create_date: datetime.datetime = Mapped.mapped_column(field_name="createdate", field_type=datetime.datetime,
                                                          order=2)
    customer_id: int = Mapped.mapped_column(field_name="customerid", field_type=int, order=3)
    customer: Customer = Mapped.mapped_reference(field_name="customerid", field_type=Customer,
                                                 reference_type=ReferenceType.Lookup)
    status: InvoiceStatus = Mapped.mapped_column(field_name="status", field_type=InvoiceStatus, order=5)
    total: float = Mapped.mapped_column(field_name="total", field_type=float, order=6, init=False)
    lines: list[InvoiceLine] = Mapped.mapped_reference(field_name="id", field_type=InvoiceLine,
                                                       join_parent_field_name="invoiceid",
                                                       reference_type=ReferenceType.OneToMany)

    def __init__(self, create_date: datetime.datetime = datetime.datetime.now(), customer_id: int = 0,
                 status: InvoiceStatus = InvoiceStatus.Initial, connection=None):
        self.create_date = create_date
        self.customer_id = customer_id
        if customer_id == 0:
            self.customer = None
        else:
            customer_type = make_typed_entity_proxy(Customer)
            self.customer = customer_type(customer_id, connection.connection_string)
        self.status = status
        self.total = 0.0
        self.lines = []

    def map_row(self, row, connection: ConnectionBase) -> TableBase:
        setattr(self, 'id', connection.map_sql_value(row[0], int))
        setattr(self, 'create_date', connection.map_sql_value(row[1], datetime.datetime))
        setattr(self, 'customer_id', connection.map_sql_value(row[2], int))
        customer_id = connection.map_sql_value(row[2], int)
        if customer_id is None:
            setattr(self, 'customer', None)
        else:
            _proxy_cls_customer = make_typed_entity_proxy(Customer)
            setattr(self, 'customer', _proxy_cls_customer(customer_id, connection.connection_string))
        setattr(self, 'status', connection.map_sql_value(row[3], InvoiceStatus))
        setattr(self, 'total', connection.map_sql_value(row[4], float))
        id = connection.map_sql_value(row[0], int)
        if id is None:
            setattr(self, 'lines', [])
        else:
            repo = RepositoryContext.get_repository(InvoiceLine)
            obj_list = []
            with SessionFactory.connect(connection.connection_string) as session:
                items = repo.fetch_id_for_parent(session, id)
                for id in items:
                    proxy = make_typed_entity_proxy(InvoiceLine)
                    obj_list.append(proxy(id, connection.connection_string))

            setattr(self, 'lines', obj_list)

        return self

    def get_insert_params(self) -> dict:
        return {"createdate": self.create_date, "customerid": self.customer_id, "status": self.status.value,
                "total": self.total}

    def get_update_params(self) -> dict:
        return {"id": self.id, "createdate": self.create_date, "customerid": self.customer_id,
                "status": self.status.value,
                "total": self.total}

    def calculate_total(self):
        self.total = 0.0
        for line in self.lines:
            self.total += line.product.price * line.quantity
