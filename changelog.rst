Project history
===============

0.0.1
-----

Initial state. Supports nested hashes and basic requests.

0.0.2
-----

Added nested lists support without insert and delete requests (positions in list
should be specified explicitly).

0.0.3
-----

Added support for insertion and deletion requests in nested lists.

0.0.4
-----

* test_database.py is split, separate module for each request is created
* some unit-tests added
* added request format checks to interface classes
* added unit-tests for interface format checks

0.0.5
-----

* greatly refactored database layer; structure and logic are still kind of tangled though
* fixed some flaws in database logic, added unittests for these cases
* each request is transacted now
* added protection from SQL injection (hid it in db engine-specific class)
* added exceptions to requests

0.0.6
-----

* added support for int, float, binary and null types along with corresponding search conditions.
* logic and structure layers separated almost completely

0.0.7
-----

* added mechanisms for creating/opening the database
* hid ID creation inside database class and made ModifyRequest return ID of the created object
* moved request tests to a higher level, so that they can be used for DBs written using different languages
* created user-friendly API for requests and connections
* added support for processing several requests inside a single transaction
* moved to Python 3.1

0.0.8
-----

* refactored database interface, hid unnecessary details of modules and classes
* refactored database internals, removed redundant request transformations (since they
  are hidden from user now)
* added functionality tests for connection (transaction functionality, explicit/implicit
  transactions, wrong parameters passed to functions)
* added insert_many(), delete_many(), read_many()

0.0.9
-----

* added helper requests (objectExists() and dump())
* added XML RPC server and client (with multicall support for asynchronous transactions)
* added parameters for test run (in-memory/real DB, API/XMLRPC calls and so on)

0.0.10
------

* using value placeholders instead of string concatenations
* added Postgre SQL engine class
* several tests structure improvements

0.0.11
------

* added fuzz test and several functionality tests (including regression tests for found bugs)
* test coverage is 100% for base logic and close to 100% for other code
* added support for empty structures (lists/dicts)

0.0.12
------

* added documenting for XML RPC server
* added db_path parameter to XML RPC server, which will specify the directory where databases
  are created (for databases which use files)
* added function for restoring database integrity (specification/refcounters table and
  listsizes table can be rebuilt using other DB contents)
* added setuptools info and registered in pypi

0.1.0 (planned)
---------------

* write proper documentation, save changelog to file in repository
* perform code review, rename public functions if necessary

TODO
====

* add XML RPC secure server and client (via HTTPS) and rewrite existing
  XML RPC server in order to avoid hacks (patch for python was sent, waiting for decision)
* add support for cross-references in text values, which will be resolved and
  auto-updated at the database level
* add strict/non-strict modes for database, when valid structure is enforced by database or by caller correspondingly
* add performance tests, analyze performance data