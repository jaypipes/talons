# -*- encoding: utf-8 -*-
#
# Copyright 2013 Jay Pipes
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

import inspect

from talons import exc
from talons.auth import interfaces

import falcon


class Middleware(object):

    def __init__(self, identifiers, authenticators, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.
        :param identifiers: List of objects that can identify a user.
        :param authenticators: List of objects that can authenticate a user.
        :param **conf:

            delay_401: If set, this will prevent a 401 Unauthorized
                       from being sent immediately back to the user if
                       identity information is missing or if authentication
                       of identity information failed. Instead, this setting
                       simply continues execution of the WSGI pipeline, and
                       leaves it up to the downstream application to determine
                       whether or not to return a 401. The downstream
                       application can check the value of the request
                       environ's 'wsgi.identified' value, which will be True
                       if some credentials were found, False otherwise.
                       Likewise, the 'wsgi.authenticated' value will be True
                       if the credentials were validated, False otherwise.

        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        self.identifiers = identifiers
        self.authenticators = authenticators
        self.delay_401 = conf.get('delay_401', False)

    def raise_401_no_identity(self):
        raise falcon.HTTPUnauthorized('Authentication required',
                                      'No identity information found.')

    def raise_401_fail_authenticate(self):
        raise falcon.HTTPUnauthorized('Authentication required',
                                      'Authentication failed.')

    def __call__(self, request, response, params):
        identified = False
        for i in self.identifiers:
            if i.identify(request):
                identified = True
                break

        request.env['wsgi.identified'] = identified
        if not identified:
            if self.delay_401:
                return
            self.raise_401_no_identity()

        identity = request.env['wsgi.identity']
        authenticated = False
        for a in self.authenticators:
            if a.authenticate(identity):
                authenticated = True
                break

        request.env['wsgi.authenticated'] = authenticated
        if not authenticated and not self.delay_401:
            self.raise_401_fail_authenticate()


def create_middleware(identify_with, authenticate_with, **conf):
    """
    Helper method to create middleware that can be supplied to Falcon's
    `falcon.API` method as a before argument.

    :param identify_with: List of objects that use the
                          `talons.auth.interfaces.Identifies`
                          interface. These objects will have their `identify`
                          method called in the order in which they are
                          specified. If the object is a class that inherits
                          from `talons.auth.interfaces.Identifies`,
                          then an object will
                          be instantiated of that class, with the configuration
                          options passed into its constructor.
    :param authenticate_with: List of objects that use the
                              `talons.auth.interfaces.Authenticates` interface.
                              These objects will have their `authenticate`
                              method called in the order in which they are
                              specified.
    :param **conf: Configuration option dictionary that will be supplied
                   to the identifiers and authenticators.

    :raises `talons.exc.BadConfiguration` if the identifiers or authenticators
            lists are empty or don't make sense.
    """
    if not isinstance(identify_with, list):
        identify_with = [identify_with]
    for x, i in enumerate(identify_with):
        if inspect.isclass(i):
            if issubclass(i, interfaces.Identifies):
                identify_with[x] = i = i(**conf)
        if not isinstance(i, interfaces.Identifies):
            msg = ("{0} is not a subclass of "
                   "`talons.auth.interfaces.Identifies`")
            msg = msg.format(i.__class__.__name__)
            raise exc.BadConfiguration(msg)

    if not isinstance(authenticate_with, list):
        authenticate_with = [authenticate_with]
    for x, a in enumerate(authenticate_with):
        if inspect.isclass(a):
            if issubclass(a, interfaces.Authenticates):
                authenticate_with[x] = a = a(**conf)
        if not isinstance(a, interfaces.Authenticates):
            msg = ("{0} is not a subclass of "
                   "`talons.auth.interfaces.Authenticates`")
            msg = msg.format(i.__class__.__name__)
            raise exc.BadConfiguration(msg)

    return Middleware(identify_with, authenticate_with, **conf)
