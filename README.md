# Db Common Lib  
Mainly for myself, switching between different database providers all the time, I wanted a consistent interface.   
Thats what this is for.  
More consistent (Think ADO.NET) db connectivity  

## Overview
Links pgsql, mysql, mssql, oracle, sqlite and cockroachdb in a common interface  
Unit tests provided to show usage  

## Exposed API

Import from `sb_db_common`:

```python
from sb_db_common import (
    SessionFactory, Session, PersistentSession,
    ConnectionBase, MySqlConnection, PgSqlConnection, MsSqlConnection, SqliteConnection,
    OracleConnection, CockroachConnection,
    ManagedCursor, ConfigBase, RepositoryBase, TableBase,
    DataException, DatatypeException,
)
from sb_db_common.entity import entity
from sb_db_common.mapped_field import Mapped
```

### Connections

**`ConnectionBase`** — Abstract base for all database connections. Holds `connection_string`, `database`, and `connection`. Subclasses implement `start()`, `commit()`, `rollback()`, `execute()`, `execute_lastrowid()`, `fetch()`, `close()`, and `map_sql_value()` (for mapping DB values to Python types). Use as a base when adding a new provider.

**`MySqlConnection`**, **`PgSqlConnection`**, **`MsSqlConnection`**, **`SqliteConnection`**, **`OracleConnection`**, **`CockroachConnection`** — Concrete connection classes for MySQL, PostgreSQL, SQL Server, SQLite, Oracle, and CockroachDB. Usually created via `SessionFactory.get_connection(connection_string)` rather than instantiated directly.

```python
from sb_db_common import SessionFactory

conn = SessionFactory.get_connection("sqlite:///path/to/db.sqlite")
conn.start()
# ... use conn.execute(), conn.fetch(), etc. ...
conn.commit()
conn.close()
```

### Session

**`Session`** — Context-managed database session. Opens the connection on `__enter__`, commits and closes on `__exit__`. Use for short-lived, transactional work.

```python
with SessionFactory.connect("sqlite:///test.db") as session:
    session.execute("INSERT INTO test(name) VALUES (:name)", {"name": "alice"})
    id = session.execute_lastrowid("INSERT INTO test(name) VALUES (:name)", {"name": "bob"})
    row = session.fetch_one("SELECT * FROM test WHERE id = :id", {"id": id})
    val = session.fetch_scalar("SELECT COUNT(*) FROM test")
# commits and closes when the block ends
```

**`PersistentSession`** — Session that reuses a single global connection (e.g. for in-memory SQLite). Does not close the connection on exit; only commits. Use when you need one long-lived connection shared across multiple session blocks.

```python
# First use: creates and keeps the connection
with SessionFactory.connect("sqlite:///memory") as session:
    session.execute("CREATE TABLE test(id INTEGER PRIMARY KEY, name TEXT)")
# Later: reuses same connection
with SessionFactory.connect("sqlite:///memory") as session:
    session.execute("INSERT INTO test(name) VALUES (:name)", {"name": "bob"})
```

**`SessionFactory`** — Creates sessions from connection strings. Call `SessionFactory.register()` once (e.g. at startup) so providers self-register. Use `SessionFactory.connect(connection_string)` to get a `Session` or `PersistentSession`.

```python
SessionFactory.register()  # typically at app startup
with SessionFactory.connect("pgsql://user:pass@localhost/mydb") as session:
    session.execute("SELECT 1")
```

### Infrastructure

**`ManagedCursor`** — Wrapper around a DB-API cursor that closes on context exit. Exposes `execute()`, `executemany()`, `fetchall()`, `fetchone()`, iteration, and properties like `description` (column names) and `rowcount`. Returned by `Connection.fetch()` / `Session.fetch()`.

```python
with SessionFactory.connect("sqlite:///test.db") as session:
    with session.fetch("SELECT id, name FROM test") as cursor:
        for row in cursor:
            print(row)
        # or: cursor.fetchall(), cursor.fetchone()
```

**`ConfigBase`** — Simple config holder with a `connection_string`. Subclass to add provider-specific or app-specific configuration.

```python
from sb_db_common import ConfigBase

class MyConfig(ConfigBase):
    def __init__(self, connection_string: str = ""):
        super().__init__(connection_string)
```

### Entity decorator and Mapped

**`@entity(table_name="...")`** — Decorator that turns a `TableBase` subclass into a full entity class. It inspects the class’s `Mapped`-declared fields and **generates** at class-definition time:

- **`__table_name__`** — Set from the decorator argument.
- **`__init__(self, ...)`** — Constructor with one argument per non–auto-increment, non-ignored field.
- **`__str__(self)`** — String of all non-ignored field values.
- **`map_row(self, row, connection)`** — Maps a result row to instance attributes using `connection.map_sql_value()` for type coercion (e.g. DB datetime → Python `datetime`).
- **`get_insert_params(self)`** — Dict of field name → value for insert (excludes auto-increment).
- **`get_update_params(self)`** — Dict of all field names → values for update.
- **`get_id_params(self)`** — Dict of primary-key field(s) → value(s).

Use `@entity(table_name="...")` on a class that subclasses `TableBase` and declares columns with **`Mapped.mapped_column(...)`**. The first time the class is built, `get_fields()` runs and the cache is populated; `generate_queries(connection)` (via repository `prepare(session)`) then fills the SQL script attributes on the class.

**`Mapped`** — Descriptor for entity columns. Use **`Mapped.mapped_column(name, field_name, field_type, order, size=50, precision=2, primary_key=False, autoincrement=False, unique=False, optional=False, default="", ignore=False)`** to declare a column. `order` is the 0-based index of the column in result rows and in generated `map_row`. `ignore=True` excludes the field from generated `__init__`, `__str__`, and param builders.

```python
import datetime
from sb_db_common import TableBase
from sb_db_common.entity import entity
from sb_db_common.mapped_field import Mapped

@entity(table_name="product")
class Product(TableBase):
    id = Mapped.mapped_column("id", "id", int, 0, primary_key=True, autoincrement=True)
    name = Mapped.mapped_column("name", "name", str, 1, 50)
    price = Mapped.mapped_column("price", "price", float, 2, precision=2)
    created = Mapped.mapped_column("created", "created", datetime.datetime, 3)
```

### RepositoryBase and TableBase (with generated scripts)

**`RepositoryBase`** — Base for repository-style access. Subclass and set `__table__` to an entity class (a `TableBase` subclass built with `@entity`). Each repository method calls **`prepare(session)`** first; if the table’s scripts are still empty, **`generate_queries(session.connection)`** runs and fills `__insert_script__`, `__update_script__`, `__fetch_by_id_script__`, etc. on the table class. The repository then uses those scripts and the entity’s generated `map_row`, `get_insert_params`, and `get_update_params`.

Provided methods: **`create_schema(session)`**, **`drop_schema(session)`**, **`schema_exists(session)`**, **`_get_by_id(session, id)`**, **`_item_exists(session, id)`**, **`fetch_one(session, query, params)`**, **`fetch(session, query, params)`**, **`count(session)`**, **`add(session, item)`**, **`update(session, item)`**, **`_delete(session, id)`**.

**`TableBase`** — Base for table entities. Defines **`get_fields()`** (cached list of `Mapped` columns, with **`_autoincrement_field`** set for `add()`) and **`generate_queries(connection)`**, which fills the script attributes (`__create_script__`, `__insert_script__`, `__update_script__`, etc.) using the connection’s `generate_*_query(table)` methods. Entity classes use the **`@entity`** decorator to get generated **`map_row`**, **`get_insert_params`**, **`get_update_params`**, and **`get_id_params`**; you do not implement these by hand when using `@entity`.

```python
from sb_db_common import RepositoryBase, SessionFactory
from sb_db_common.entity import entity
from sb_db_common.mapped_field import Mapped

# Entity (see example above)
@entity(table_name="product")
class Product(TableBase):
    id = Mapped.mapped_column("id", "id", int, 0, primary_key=True, autoincrement=True)
    name = Mapped.mapped_column("name", "name", str, 1, 50)
    # ...

class ProductRepo(RepositoryBase):
    __table__ = Product

repo = ProductRepo()
with SessionFactory.connect("sqlite:///app.db") as session:
    repo.prepare(session)  # or let add/fetch/etc. call it
    repo.create_schema(session)
    p = Product(name="widget", price=9.99)
    repo.add(session, p)   # p.id set if auto-increment
    one = repo._get_by_id(session, {"id": 1})
    items = repo.fetch(session, "SELECT * FROM product WHERE name = :name", {"name": "widget"})
    repo.update(session, p)
```

### Exceptions

**`DataException`** — Base exception for data-layer errors (e.g. invalid connection string, invalid id).

**`DatatypeException`** — Subclass of `DataException` for type/conversion errors.

```python
from sb_db_common import DataException, DatatypeException

try:
    SessionFactory.get_connection("unknown://x")
except DataException as e:
    print(e)
```

## Usage
Connection string format is: `<provider>://<username>:<password>@<host>/<database>`  
The supported providers are:
`sqlite, mysql, mssql, pgsql, oracle, cockroach`

The providers self-register. Call `SessionFactory.register()` before use.

```
with SessionFactory.connect(<connection string>) as session:
    id = session.execute_lastrowid("insert into test(name) values (:name);", {"name": "bob"})
    session.execute("update test set name = :name where id = :id", {"id": id, "name": "bob1"})
```

The session closes and commits automatically when it goes out of scope.  
For more control, manually call commit and rollback.

The queries are db specific, but the mechanisms are the same for all.  
Major differences are the different field types, the parameter specification and in the use of identity columns across the different db's.  
Remember to add `returning <field>` to the insert statement for pgsql or you won't get the identity back.  

### Differences 
#### sqlite
```
CREATE TABLE test(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
    name TEXT
);
```
`INSERT INTO test(name) VALUES (:name)`
#### mysql 
```
CREATE TABLE test(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(50) NULL
);
```
`INSERT INTO test(name) VALUES (%(name)s);`
#### pgsql
```
CREATE TABLE test(
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
    name VARCHAR(50) NULL
 );
 ```
`INSERT INTO test(name) VALUES (%(name)s) RETURNING id;`

#### oracle
```
CREATE TABLE test(
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    name VARCHAR(50) NULL
 );
 ```
`INSERT INTO test(name) VALUES (:name) RETURNING id;`

#### mssql
```
CREATE TABLE test(
    id INT IDENTITY(1,1) NOT NULL PRIMARY KEY, 
    name VARCHAR(50) NULL
 );
 ```
`INSERT INTO test(name) output inserted.id VALUES (%(name)s);`

Integrated security is supported, either by passing in a windows username / password, or by setting `trusted_connection=yes` - username / password are then optional, it will then ignore them if provided, and will use the current logged in user.  

## Building
`python -m build `

## Deploying
`python -m twine upload --repository pypi dist/*`