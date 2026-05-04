# Db Common Lib  
Mainly for myself, switching between different database providers all the time, I wanted a consistent interface.   
Thats what this is for.  
More consistent (Think ADO.NET) db connectivity  

## Overview
Links pgsql, mysql, mssql, oracle, sqlite and cockroachdb in a common interface.  
Unit tests show usage.  

This package focuses on **connections and sessions** (execute, fetch, transactions). It does **not** include an ORM, entity decorator, or repository layer; map rows and SQL yourself in your application.

## Exposed API

Import from `sb_db_common`:

```python
from sb_db_common import (
    SessionFactory, Session, PersistentSession,
    ConnectionBase, MySqlConnection, PgSqlConnection, MsSqlConnection, SqliteConnection,
    OracleConnection, CockroachConnection,
    ManagedCursor,
    DataException, DatatypeException,
    resolve_type,
)
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

### Utilities (`sb_db_common.utils`)

Helpers such as path/string utilities and **`resolve_type(type_name: str) -> type`**, which resolves a built-in name (e.g. `"int"`) or a fully qualified type (e.g. `"datetime.datetime"`). Import from the package root:

```python
from sb_db_common import resolve_type

t = resolve_type("datetime.datetime")
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
