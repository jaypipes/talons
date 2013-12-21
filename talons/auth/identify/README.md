What is `talons.auth.identify`?
===============================

`talons.auth.identify` contains classes that identify the user who wishes to
be authenticated. Each class derives from `talons.auth.Identifies`. Each
class implements a single method, `identify()`, that takes the
incoming `falcon.request.Request` object as its sole parameter. If the
identity of the authenticating user can be determined, then the Identifier
object stores a `talons.auth.Identity` object in the WSGI environ's
`wsgi.identity` key. Multiple Identifier classes can be supplied to the
`talons.auth.create_middleware` method to support a variety of ways of
gleaning identity information from the WSGI request. Each Identifier's
`identify()` method checks to see if the `wsgi.identity` key is already
set in the WSGI environs. If it is, the method simply returns True.

`talons.auth.identify.basicauth.Identifier`
===========================================

The most basic identifier, `talons.auth.identify.basicauth.Identifier` has no
configuration options and simply looks in the
[`Authenticate`](http://en.wikipedia.org/wiki/Basic_access_authentication) HTTP
header for credential information. If the `Authenticate` HTTP header is found
and contains valid credential information, then that identity information is
stored in the `wsgi.identity` WSGI environs key.

`talons.auth.identify.httpheader.Identifier`
============================================

Another simple identifier, `talons.auth.identify.httpheader.Identifier` looks
for configurable HTTP headers in the incoming WSGI request, and uses the values
of the HTTP headers to construct a `talons.auth.Identity` object.

A set of configuration options control how this Identifier class behaves:

 * `identify_httpheader_user`: HTTP header to look for user/login
   name (required)
 * `identify_httpheader_key`: HTTP header to look for password/key
   (required)
 * `identify_httpheader_$ATTRIBUTE`: HTTP header that, if found, will
   be used to add $ATTRIBUTE to the Identity object stored in the WSGI
   pipeline. (optional)

The above configuration options are supplied to the constructor as keyword
arguments.

Example
-------

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
identify_httpheader_user=x-auth-user
identify_httpheader_key=x-auth-password
identify_httpheader_domain=x-auth-domain
```
