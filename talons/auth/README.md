What is `talons.auth`?
======================

`talons.auth` is middleware for Falcon that provides pluggable authentication
and authorization capabilities to the Falcon API application pipeline that
the middleware is attached to.

There are a variety of plugins that handle identification of the user making
an API request and authenticating credentials with a number of common backends,
including LDAP and SQL data stores.

Authentication involves two main tasks:

 * Identifying the user who wishes to be authenticated
 * Validating credentials for the identified user

`talons.auth` contains different modules for each task.

`talons.auth.identify` contains modules for grabbing identity information
from some standard mechanisms like the HTTP Authentication header or from some
other HTTP headers.

`talons.auth.authenticate` contains modules that can validate the identity
information retrieved from a `talons.auth.identify` module by querying
various backend data stores like LDAP or an SQL database.

To give your Falcon-based WSGI application authentication capabilities, you
simply create middleware that has one or more `talons.auth.identify` modules
and one or more `talons.auth.authenticate` modules. We even give you a helper
method to create such middleware in a single call.


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
from talons import auth
from talons.auth.identify import basicauth, httpheader
from talons.auth.authenticate import ldap

# Assume getappconfig() returns a dictionary of application configuration
# options that may be read from some INI file...
config = getappconfig()

auth_middleware = auth.create_middleware(identify_with=[
                                            basicauth.Identifier,
                                            httpheader.Identifier],
                                         authenticate_with=ldap.Authenticator,
                                         **config)

app = falcon.API(before=[auth_middleware])
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
* No Paste.
* Wanted something that fit Falcon's app construction paradigm.

But hey, there's nothing inherently wrong with repoze.who. If you like it, and it works
for you, use it.
