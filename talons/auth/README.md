What is `talons.auth`?
======================

`talons.auth` is middleware for Falcon that provides pluggable authentication
and authorization capabilities to the Falcon API application pipeline that
the middleware is attached to.

There are a variety of plugins that handle identification of the user making
an API request and authenticating credentials with a number of common backends,
including LDAP and SQL data stores.

How to Use `talons.auth`
========================

A simple Falcon API application is constructed like so:

```python
import falcon

# falcon.API instances are callable WSGI apps
app = falcon.API()
```

To add middleware to a Falcon API application, we simply instantiate the
desired `talons.auth` middleware and supply it to the `falcon.API()` call:

```python
import falcon
from talons.auth import ldap

# Assume getappconfig() returns a dictionary of application configuration
# options that may be read from some INI file...
config = getappconfig()

ldap_middleware = ldap.Middleware(**config)

app = falcon.API(before=[ldap_middleware])
```


Why `talons.auth`?
==================

Why not just use middleware like [repose.who](http://docs.repoze.org/who/2.0/index.html) for
authentication plugins? Why re-invent the wheel here?

A few reasons, in no particular order:

* Use of the Webob library. I'm not a fan of it, as I've run into numerous issues with
  this library over the years.
* Use of zope.interfaces. Also not a fan of it. It's a library that seems to be designed
  for traditional C++ programmers instead of feeling like it's designed for Python developers.
  Just use the [abc](http://docs.python.org/2/library/abc.html) module if you absolutely must
  have strict interface enforcement.
* Trying to override things like logging setup in constructors of middleware.

But hey, there's nothing inherently wrong with repoze.who. If you like it, and it works
for you, use it.
