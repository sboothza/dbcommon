from parent_child import Product, Customer, Invoice, InvoiceLine
from sb_db_common import RepositoryBase, Session, TableBase
from sb_db_common.repo_context import RepositoryContext


class ProductRepository(RepositoryBase):
    __table__ = Product

    def find_by_name(self, session, name: str) -> Product:
        return self.fetch_one(session, "select id, name, description, quantity, price from Product where name = :name",
                              {"name": name})


RepositoryContext.register_repository(ProductRepository)


class CustomerRepository(RepositoryBase):
    __table__ = Customer

    def find_by_name(self, session, name: str) -> Customer:
        return self.fetch_one(session, "select id, name, email, phone, address from Customer where name = :name",
                              {"name": name})


RepositoryContext.register_repository(CustomerRepository)


class InvoiceRepository(RepositoryBase):
    __table__ = Invoice

    def find_by_name(self, session, name: str) -> list[Invoice]:
        return self.fetch(session,
                          "select i.id, i.createdate, i.customerid, i.status, i.total from Invoice i inner join customer c on i.customerid = c.id where c.name = :name",
                          {"name": name})

    def update(self, session: Session, item: Invoice):
        super().update(session, item)
        invoiceline_repo: InvoiceLineRepository = RepositoryContext.get_repository(InvoiceLine)
        for line in item.lines:
            invoiceline_repo.add(session, line)


RepositoryContext.register_repository(InvoiceRepository)


class InvoiceLineRepository(RepositoryBase):
    __table__ = InvoiceLine

    def add(self, session: Session, item: InvoiceLine) -> TableBase:
        new_item = item
        if item.id is int and self._item_exists(session, item.id):
            super().update(session, item)
        else:
            new_item = super().add(session, item)

        return new_item


RepositoryContext.register_repository(InvoiceLineRepository)
