import datetime
import unittest

from parent_child import Product, Customer, Invoice, InvoiceStatus, InvoiceLine
from parent_child_repo import CustomerRepository, ProductRepository
from sb_db_common import SessionFactory
from sb_db_common.repo_context import RepositoryContext


class TestParentChild(unittest.TestCase):
    def setUp(self):
        self.connection_string = "sqlite://:memory:"
        self.seed()

    def seed(self):
        with SessionFactory.connect(self.connection_string) as session:
            product_repo = RepositoryContext.get_repository(Product)
            if not product_repo.schema_exists(session):
                product_repo.create_schema(session)

            product_repo.add(session, Product("widget1", "Widget 1", 100, 10))
            product_repo.add(session, Product("widget2", "Widget 2", 200, 20))

            customer_repo = RepositoryContext.get_repository(Customer)
            if not customer_repo.schema_exists(session):
                customer_repo.create_schema(session)
            customer_repo.add(session, Customer("Stephen", "stephen_email", "stephen_phone", "stephen_address"))
            customer_repo.add(session, Customer("Tamrin", "tamrin_email", "tamrin_phone", "tamrin_address"))

            invoice_repo = RepositoryContext.get_repository(Invoice)
            if not invoice_repo.schema_exists(session):
                invoice_repo.create_schema(session)

            invoice_line_repo = RepositoryContext.get_repository(InvoiceLine)
            if not invoice_line_repo.schema_exists(session):
                invoice_line_repo.create_schema(session)

    def test_complete(self):
        with SessionFactory.connect(self.connection_string) as session:
            customer_repo: CustomerRepository = RepositoryContext.get_repository(Customer)
            customer1 = customer_repo.find_by_name(session, "Stephen")
            product_repo: ProductRepository = RepositoryContext.get_repository(Product)
            product1 = product_repo.find_by_name(session, "widget1")
            product2 = product_repo.find_by_name(session, "widget2")
            invoice_repo = RepositoryContext.get_repository(Invoice)

            invoice1: Invoice = invoice_repo.add(session,
                                                 Invoice(datetime.datetime.now(), customer1.id, InvoiceStatus.Pending, session.connection))
            invoice1.lines.append(InvoiceLine(invoice1.id, datetime.datetime.now(), product1.id, 5, session.connection))
            invoice1.lines.append(InvoiceLine(invoice1.id, datetime.datetime.now(), product2.id, 5, session.connection))
            invoice1.calculate_total()
            invoice_repo.update(session, invoice1)

            invoice1 = invoice_repo._get_by_id(session, invoice1.id)
            self.assertEqual(len(invoice1.lines), 2)
            self.assertEqual(invoice1.total, 150)

            invoice1.calculate_total()
            self.assertEqual(invoice1.total, 150)
