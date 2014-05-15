# -*- encoding: utf-8 -*-
#
# Copyright 2013-2014 Jay Pipes
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


class Identity(object):

    """
    Concrete class that exposes identity information as well as
    credentials and authorization information (like roles and group
    membership).
    """

    def __init__(self, login, key=None, roles=[], groups=[]):
        self.login = login
        self.key = key
        self.groups = set(groups)
        self.roles = set(roles)


class ResourceAction(object):

    """
    Concrete class that exposes identity information as well as
    credentials and authorization information (like roles and group
    membership).
    """

    def __init__(self, request, params):
        """
        Constructs a ResourceAction object from a `falcon.request.Request`
        object and a dict of params.

        The ResourceAction object is used by various plugins to describe the
        HTTP request in a static descriptor way.

        :param request: The `falcon.request.Request` object representing the
                        HTTP request to a falcon app.
        :param params: A dict of parameters that was parsed by the falcon
                       app from the requested URI. The parameters represent
                       matched field expressions that the responder object's
                       path_template matched at routing time.
        """
        self.request = request
        self.params = params
        path = request.env['PATH_INFO']
        # Cut off the query string
        path = path.split('?')[0]
        self._dot_string = path.replace('/', '.').strip('.') + '.'
        self._dot_string = self._dot_string + request.method.lower()

    def to_string(self):
        """
        Returns a string in a dotted-notation format that describes the HTTP
        request that was made to the Falcon app. The HTTP method is always
        the last element of the dotted-notation string.

        As an example, if an HTTP request was made to:

          GET /users/123/groups/ABC

        The `talons.resource.Resource` object that would be constructed from
        the Falcon request would return the following from the `to_string`
        method:

          users.123.groups.ABC.get

        Likewise, an HTTP request to:

          POST /orgs

        would yield this string from `to_string`:

          orgs.post
        """
        return self._dot_string


class Identifies(object):

    """
    Base class for plugins that act to identify the requesting user,
    possibly by inspecting headers in the incoming HTTP request or
    looking in the wsgi.environ.
    """

    IDENTITY_ENV_KEY = 'wsgi.identity'

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf: Free-form keyword arguments. Concrete
                       implementations should document the keyword arguments
                       that the plugin cares about.
        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        pass

    def identify(self, request):
        """
        Looks and stores identity information in the request environ's
        'wsgi.identity' key. If no identity information is found, this
        key shall be set to None.
        """
        raise NotImplementedError  # pragma: NO COVER


class Authenticates(object):

    """
    Base class for plugins that act to authenticate the identified credentials
    """

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf: Free-form keyword arguments. Concrete
                       implementations should document the keyword arguments
                       that the plugin cares about.
        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        pass

    def authenticate(self, identity):
        """
        Looks at the supplied identity object and returns True if the
        credentials can be verified, False otherwise. If the plugin also
        retrieves role or group information, it may modify the supplied
        Identity object.
        """
        raise NotImplementedError  # pragma: NO COVER

    def sets_roles(self):
        """
        Returns True if the authenticator plugin decorates the Identity
        object with a set of roles, False otherwise.
        """
        return False  # pragma: NO COVER

    def sets_groups(self):
        """
        Returns True if the authenticator plugin decorates the Identity
        object with a set of groups, False otherwise.
        """
        return False  # pragma: NO COVER


class Authorizes(object):

    """
    Base class for plugins that act to authorize an identity to perform
    an action against a particular resource.
    """

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf: Free-form keyword arguments. Concrete
                       implementations should document the keyword arguments
                       that the plugin cares about.
        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        pass

    def authorize(self, identity, resource, action):
        """
        Looks at the supplied identity object and returns True if the
        identity has the authority to perform the supplied action against
        the supplied resource, False otherwise.

        :param identity: The `talons.auth.interfaces.Identity` object for
                         which we should determine authorization.
        :param resource: A `talons.resource.Resource` object that describes the
                         resource that the identity is attempting to perform
                         the action against.
        :param action: A string describing the action that should be checked
                       for authorization.
        """
        raise NotImplementedError  # pragma: NO COVER
