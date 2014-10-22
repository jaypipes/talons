# Talons == Falcon Hooks [![Build Status](https://travis-ci.org/talons/talons.png)](https://travis-ci.org/talons/talons)

Talons is a library of WSGI middleware that is designed to work with
the [Falcon](http://github.com/racker/falcon) lightweight Python framework
for building RESTful APIs. Like Falcon, Talons aims to be fast, light, and
flexible.

The first middleware in Talons is authentication middleware, enabling one
or more backend identity plugins to handle authentication.

# What is `talons.auth`?

`talons.auth` is a namespace package that contains utilies for
constructing identifying and authenticating middleware and plugins
designed for applications running the Falcon WSGI micro-framework
for building REST APIs.

## A simple usage example

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
from talons.auth import middleware
from talons.auth import basicauth, httpheader, htpasswd

# Assume getappconfig() returns a dictionary of application configuration
# options that may have been read from some INI file...
config = getappconfig()

auth_middleware = middleware.create_middleware(identify_with=[
                                                 basicauth.Identifier,
                                                 httpheader.Identifier],
                                               authenticate_with=htpasswd.Authenticator,
                                               **config)

app = falcon.API(before=[auth_middleware])
```

# Details

There are a variety of basic plugins that handle identification of the user making
an API request and authenticating credentials with a number of common backends,
including LDAP and SQL data stores.

Authentication involves two main tasks:

 * Identifying the user who wishes to be authenticated
 * Validating credentials for the identified user

Classes that derive from `talons.auth.interfaces.Identifies` implement an `identify`
method that takes the `falcon.request.Request` object from the WSGI pipeline and
looks at elements of the request to determine who the requesting user is.

The class that stores credential information -- including a login, password/key,
a set of roles or groups, as well as other metadata about the requesting user --
is the `talons.auth.interfaces.Identity` class. `talons.auth.interfaces.Identifies`
subclasses store this `Identity` object in the WSGI environs' "wsgi.identity" bucket.

Classes that derive from `talons.auth.interfaces.Authenticates` implement an
`authenticate` method that takes a single argument -- a `talons.auth.interfaces.Identity`
object -- and attempts to validate that the identity is authentic.

To give your Falcon-based WSGI application authentication capabilities, you
simply create middleware that has one or more `talons.auth.identify` modules
and one or more `talons.auth.authenticate` modules. We even give you a helper
method -- `talons.auth.middleware.create_middleware` -- to create such middleware
in a single call.

## Identifiers

Each class that derives from `talons.auth.interfaces.Identifies` is called an "Identifier". Each
class implements a single method, `identify()`, that takes the incoming `falcon.request.Request`
object as its sole parameter. If the identity of the authenticating user can be determined,
then the Identifier object stores a `talons.auth.interfaces.Identity` object in the WSGI environ's
`wsgi.identity` key and returns True.

Multiple Identifier classes can be supplied to the
`talons.auth.middleware.create_middleware` method to support a variety of ways of
gleaning identity information from the WSGI request. Each Identifier's
`identify()` method checks to see if the `wsgi.identity` key is already
set in the WSGI environs. If it is, the method simply returns True and does
not attempt to process anything further.

### `talons.auth.basicauth.Identifier`

The most basic identifier, `talons.auth.basicauth.Identifier` has no
configuration options and simply looks in the
[`Authenticate`](http://en.wikipedia.org/wiki/Basic_access_authentication) HTTP
header for credential information. If the `Authenticate` HTTP header is found
and contains valid credential information, then that identity information is
stored in the `wsgi.identity` WSGI environs key.

### `talons.auth.httpheader.Identifier`

Another simple identifier, `talons.auth.httpheader.Identifier` looks
for configurable HTTP headers in the incoming WSGI request, and uses the values
of the HTTP headers to construct a `talons.auth.Identity` object.

A set of configuration options control how this Identifier class behaves:

 * `httpheader_user`: HTTP header to look for user/login
   name (required)
 * `httpheader_key`: HTTP header to look for password/key
   (required)
 * `httpheader_$ATTRIBUTE`: HTTP header that, if found, will
   be used to add $ATTRIBUTE to the Identity object stored in the WSGI
   pipeline. (optional)

The above configuration options are supplied to the constructor as keyword
arguments.

#### Example

Suppose we wanted to extract identity information from the following HTTP
Headers:

 * `X-Auth-User` -- The value of this header will be the authenticating user's
   user name
 * `X-Auth-Password` -- The value of this header will be the authenticating
   user's password
 * `X-Auth-Domain` -- The value of this header should be considered the
   authentication domain that will be considered when authenticating the
   identity. We want to store this value on the `talons.auth.Identity` object's
   `domain` attribute.

Our configuration options would look like this:

```
httpheader_user=x-auth-user
httpheader_key=x-auth-password
httpheader_domain=x-auth-domain
```

## Authenticators

Each class that derives from `talons.auth.interfaces.Authenticates` is
called an "Authenticator". Each Authenticator implements a single method,
`authenticate()`, that takes a `talons.auth.interfaces.Identity` object
as its sole parameter.

The `authenticate` method verifies that the supplied identity can be
verified (authenticated). Different implementations will rely on various
backend storage systems to validate the incoming identity/credentials.
If authentication was successful, the method returns True, False otherwise.

Talons comes with a few simple examples of Authenticator plugins.

### `talons.auth.external.Authenticator`

A generic Authenticator plugin that has one main configuration option,
`external_authn_callable` which should be the "module.function" or
"module.class.method" dotted-import notation for a function or class
method that accepts a single parameter. This function will be called by
the instance of `talons.auth.authenticate.external.Authenticator` to
validate the credentials of a request.

In addition, there are two other configuration options that indicate
whether the `external_authfn` function may set the roles or groups
attributes on the supplied identity:

 * `external_sets_roles`: Boolean (defaults to False). A True value
   indicates the plugin may set the roles attribute on the identity
   object.

 * `external_sets_groups`: Boolean (defaults to False). A True value
   indicates the plugin may set the groups attribute on the identity
   object.

#### Example

Suppose we have some application code that looks up a stored password
for a user in a [`Redis`](http://redis.io) Key-Value Store. Salted, encrypted
passwords for each user are stored in the Redis KVS, along with a
comma-separated list of roles the user belongs to.

Our application has a Python file called `/application/auth.py` that looks
like this:

```python
import hashlib

import redis

_AUTH_DB = redis.StrictRedis(host='localhost', port=6379, db=0)


def _pass_matches_stored_pass(pass, stored_pass):
    # Assume that passwords are stored in Redis in the following format:
    # salt:hashedpass
    # and that the passwords have been hashed with SHA-256
    salt, stored_hashed_pass = stored_pass.split(':')
    hashed_pass = hashlib.sha256(salt.encode() + pass.encode()).hexdigest()
    return hashed_pass == stored_hashed_pass


def authenticate(identity):
    user = identity.login
    pass = identity.key

    # Assume that user "records" are stored in Redid in the following format:
    # salt:hashedpass#roles
    # Where roles is a comma-separated list of roles
    user_record = _AUTH_DB.get(user)
    if user_record:
        stored_pass, role_list = user_record.split('#')
        auth_success = _pass_matches_stored_pass(pass, stored_pass)
        if auth_success:
            identity.roles = role_list.split(',')
    return auth_success
```

To use the above `application.auth.authenticate` method for authenticating
identities, we'd supply the following configuration options to the
`talons.auth.external.Authenticator` constructor:

 * `external_authn_callable=application.auth.authenticate`
 * `external_sets_roles=True`

### `talons.auth.htpasswd.Authenticator`

An Authenticator plugin that queries an Apache htpasswd file to check
the credentials of a request. The plugin has a single configuration option:

 * `htpasswd_path`: The filepath to the Apache htpasswd file to
   use for authentication checks.

## Authorizers

Each class that derives from `talons.auth.interfaces.Authorizes` is
called an "Authorizer". Each Authorizer implements a single method,
`authorize()`, that takes a `talons.auth.interfaces.Identity` object,
and a `talons.auth.interfaces.ResourceAction` object.

The `ResourceAction` object currently has a single method, `to_string`,
that returns a "dotted-notation" string describing the requested
HTTP resource.

For instance, let's say the identity made an HTTP request to:

    POST /users/12345/groups

The `ResourceAction.to_string` method that is supplied to the `authorize`
function would yield the string "users.12345.groups.post". This string is
useful to plugins that compare the string with the supplied identity object.
See below for an example that makes this more clear.

At present, there is only a single Authorizer built in to Talons: the
`talons.auth.external.Authorizer` class. Like its sister, the
`talons.auth.external.Authenticator`, it accepts an external callable that
accepts the identity and resource action parameters and returns whether
the identity is allowed to perform the action on the resource. The single
configuration parameter is called `external_authz_callable`.

Let's continue the example from above and add an external callable that
will be used as an authorizer. This callable will compare the result of
the `ResourceAction`'s `to_string` method against the supplied identity
object and a hashmap of regular expressions in order to determine if the
user is permitted to perform an action.

Assuming our application has a Python file called `/application/auth.py` that
contains the above authenticate code, as well as this:
like this:

```python
import re


def self_or_admin(match, identity):
    """
    Returns True if the identity has an admin role or the identity
    matches the requesting user.
    """
    if "admin" in identity.roles:
        return True
    return match.groups(1) == identity.login


def anyone(*args):
    return True


_POLICY_RULES = [
    (r'^users\.(^\.)+\.get$', self_or_admin),
    (r'^users\.post$', anyone),
]
POLICIES = []
for regex, fn in _POLICY_RULES:
    POLICIES.append((re.compile(regex), fn))


def authorize(identity, resource_action):
    user = identity.login
    res_string = resource_action.to_string()
    for p, fn in _POLICIES:
        m = p.match(res_string)
        if m:
            return fn(m, identity)
```

To use the above `application.auth.authorize` method for authorizing the
identity that was authenticated, we'd supply the following configuration
options to the `talons.auth.external.Authorizer` constructor:

 * `external_authz_callable=application.auth.authorize`


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

## Contributing

[Jay Pipes](http://joinfu.com) maintains the Talons library. You can usually find him on the Freenode IRC #openstack-dev
channel. Interested in improving and enhancing Talons? Pull requests are always welcome.

## License and Copyright

Copyright 2013-2014, Jay Pipes

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing permissions and limitations under
the License.
