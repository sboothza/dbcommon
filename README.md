# Db Common Lib  
Mainly for myself, switching between different database providers all the time, I wanted a consistent interface.   
Thats what this is for.  
More consistent (Think ADO.NET) db connectivity  

## Overview
Links pgsql, mysql, mssql, oracle and sqlite in a common interface  
Unit tests provided to show usage  

## Exposed API

Import from `sb_db_common`:

```python
from sb_db_common import (
    SessionFactory, Session, PersistentSession,
    ConnectionBase, MySqlConnection, PgSqlConnection, MsSqlConnection, SqliteConnection, OracleConnection, 
    ManagedCursor, ConfigBase, RepositoryBase, TableBase,
    DataException, DatatypeException,
)
```

### Connections

**`ConnectionBase`** — Abstract base for all database connections. Holds `connection_string`, `database`, and `connection`. Subclasses implement `start()`, `commit()`, `rollback()`, `execute()`, `execute_lastrowid()`, `fetch()`, and `close()`. Use as a base when adding a new provider.

**`MySqlConnection`**, **`PgSqlConnection`**, **`MsSqlConnection`**, **`SqliteConnection`**, **`OracleConnection`** — Concrete connection classes for MySQL, PostgreSQL, SQL Server, and SQLite. Usually created via `SessionFactory.get_connection(connection_string)` rather than instantiated directly.

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

**`RepositoryBase`** — Base for repository-style access. Subclass and set `__table__` to a `TableBase` subclass. Provides `create_schema()`, `drop_schema()`, `schema_exists()`, `_get_by_id()`, `_item_exists()`, `fetch_one()`, `fetch()`, `count()`, `add()`, `update()`, `_delete()` using the table’s scripts and `map_row()`.

```python
from sb_db_common import RepositoryBase, TableBase, Session

class MyTable(TableBase):
    __table_name__ = "mytable"
    __create_script__ = "CREATE TABLE mytable(id INT PRIMARY KEY, name TEXT);"
    # ... __insert_script__, __update_script__, __fetch_by_id_script__, etc.
    def map_row(self, row): ...
    def get_insert_params(self): ...
    def get_update_params(self): ...
    def get_id_params(self): ...

class MyRepo(RepositoryBase):
    __table__ = MyTable

repo = MyRepo()
with SessionFactory.connect("sqlite:///test.db") as session:
    repo.create_schema(session)
    n = repo.count(session)
```

**`TableBase`** — Base for table entities. Subclass and set class attributes for DDL/DML scripts (`__create_script__`, `__insert_script__`, `__update_script__`, `__fetch_by_id_script__`, etc.) and implement `map_row()`, `get_insert_params()`, `get_update_params()`, `get_id_params()` so repositories can map rows to objects and build parameters.

```python
class Product(TableBase):
    __table_name__ = "product"
    __fetch_by_id_script__ = "SELECT id, name FROM product WHERE id = :id"
    def map_row(self, row): ...
    def get_insert_params(self): ...
    def get_update_params(self): ...
    def get_id_params(self): ...
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
`sqlite, mysql, mssql, pgsql, oracle`

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
    id id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
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