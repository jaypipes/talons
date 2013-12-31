What is `talons.auth.authenticate`?
===================================

`talons.auth.authenticate` contains classes that subclass
from `talons.auth.Authenticates`. Each class implements a single method,
`authenticate()`, that takes a `talons.auth.Identity` object as its sole
parameter.

The `authenticate` method verifies that the supplied identity can be
verified (authenticated). Different implementations will rely on various
backend storage systems to validate the incoming identity/credentials.
If authentication was successful, the method returns True, False otherwise.

Talons comes with a few simple examples of plugins that implement
`talons.auth.Authenticates`.

`talons.auth.authenticate.external.Authenticator`
=================================================

A generic Authenticator plugin that has a single configuration option,
`authenticate_external_authfn` which should be the "module.function" or
"module.class.method" dotted-import notation for a function or class
method that accepts a single parameter. This function will be called by
the instance of `talons.auth.authenticate.external.Authenticator` to
validate the credentials of a request.

Example
-------

Suppose we have some application code that looks up a stored password
for a user in a [`Redis`](http://redis.io) Key-Value Store. Salted, encrypted
passwords for each user are stored in the Redis KVS.

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

    stored_pass = _AUTH_DB.get(user)
    if stored_pass:
        return _pass_matches_stored_pass(pass, stored_pass)
    return False
```

To use the above `application.auth.authenticate` method for authenticating
identities, we'd supply the following configuration options to the
`talons.auth.authenticate.external.Authenticator` constructor:

 * `authenticate_external_authfn=application.auth.authenticate`

`talons.auth.authenticate.htpasswd.Authenticator`
=================================================

An Authenticator plugin that queries an Apache htpasswd file to check
the credentials of a request. The plugin has a single configuration option:

 * `authenticate_htpasswd_path`: The filepath to the Apache htpasswd file to
   use for authentication checks.
