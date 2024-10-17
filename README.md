# Db Common Lib  
Mainly for myself, switching between different database providers all the time, I wanted a consistent interface.   
Thats what this is for.  
More consistent (Think ADO.NET) db connectivity  

## Overview
Links psgsql, mysql and sqlite in a common interface  
Unit tests provided to show usage  

## Usage
Connection string format is: `<provider>://<username>:<password>@<host>/<database>`  
The supported providers are:
`sqlite, mysql, pgsql`

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



## Building
`python -m build `

## Deploying
`python -m twine upload --repository pypi dist/*`