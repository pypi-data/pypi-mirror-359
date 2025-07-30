ktpanda_modules
===============

A collection of helper modules by PinkPandaKatie (https://ktpanda.org)


threadpool
----------

Maintains a pool of threads which can execute jobs.


object_pool
-----------

Maintains a pool of objects which can be checked out as needed by different threads.


hotload
-------

A class which can reload its methods from a module when it detects changes.


sqlite_helper
-------------

A wrapper class for an SQLite database that includes schema versioning and
various helper methods.

textcolor
---------

A module for coloring text using VT100 codes


ttyutil
-------

Utilities for controlling Posix TTY devices and reading raw input.


dateutils
---------

Simple utilities for dealing with date / time, extending the built-in datetime.


fileutils
---------

Simple utilities for dealing with files / directories.

roundtrip_encoding
------------------

Contains functions for converting between text and binary data in a way that unmodified
text data will be converted to the same binary data.

vt100
-----

Defines constants for VT100 control codes.


cli
---

Defines decorators which make it easy to create dispatch-style CLI interfaces.

xmledit
-------

Parses an XML document using Expat, and allows replacing nodes and text without affecting
the surrounding formatting.

dictutils
---------

Various dictionary subclasses

dsl
---

Utility class for implementing a Python-based DSL
