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
import logging

from talons import exc
from talons import helpers
from talons.auth import interfaces

LOG = logging.getLogger(__name__)


class Authenticator(interfaces.Authenticates):

    """
    Authenticates the supplied Identity by calling out to an external
    authentication function.
    """

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf:

            external_authn_callable: Dotted-notation module.class.method
                             or module.function that will be used
                             to authenticate. This function will
                             accept as its only argument the
                             `talons.interfaces.auth.Identity` object.
            external_sets_roles: Boolean (defaults to False) of whether the
                                 external authentication function will set the
                                 roles attribute of the Identity object.
            external_sets_groups: Boolean (defaults to False) of whether the
                                  external authentication function will set
                                  the groups attribute of the Identity object.

        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        authfn = conf.pop(
            'external_authn_callable',
            conf.pop('external_authfn', None)
        )  # Backwards-compat

        if not authfn:
            msg = ("Missing required external_authfn "
                   "configuration option.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        # Try import'ing the auth function to ensure that it exists
        try:
            self.authfn = helpers.import_function(authfn)
        except (TypeError, ImportError):
            msg = ("external_authfn either could not be found "
                   "or was not callable.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        # Ensure that the auth function signature is what we expect
        spec = inspect.getargspec(self.authfn)
        if len(spec[0]) != 1:
            msg = ("external_authfn has an invalid function "
                   "signature. The function must take only a single "
                   "parameter.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        self._sets_roles = conf.get('external_sets_roles', False)
        self._sets_groups = conf.get('external_sets_groups', False)

    def authenticate(self, identity):
        """
        Looks at the supplied identity object and returns True if the
        credentials can be verified, False otherwise.
        """
        return self.authfn(identity)

    def sets_roles(self):
        """
        Returns True if the authenticator plugin decorates the Identity
        object with a set of roles, False otherwise.
        """
        return self._sets_roles

    def sets_groups(self):
        """
        Returns True if the authenticator plugin decorates the Identity
        object with a set of groups, False otherwise.
        """
        return self._sets_groups


class Authorizer(interfaces.Authorizes):

    """
    Authorizes the supplied Identity and ResourceAction by calling out to
    an external function.
    """

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf:

            external_authz_callable: Dotted-notation module.class.method
                              or module.function that will be used
                              to authorize. This function will
                              accept as its only two arguments a
                              `talons.interfaces.auth.Identity` object
                              and a `talons.interfaces.auth.RequestAction`
                              object.

        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        authfn = conf.pop('external_authz_callable', None)
        if not authfn:
            msg = ("Missing required external_authz_callable "
                   "configuration option.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        # Try import'ing the auth function to ensure that it exists
        try:
            self.authfn = helpers.import_function(authfn)
        except (TypeError, ImportError):
            msg = ("external_authz_callable either could not be found "
                   "or was not callable.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        # Ensure that the auth function signature is what we expect
        spec = inspect.getargspec(self.authfn)
        if len(spec[0]) != 2:
            msg = ("external_authz_callable has an invalid function "
                   "signature. The function must take two arguments: "
                   "an identity and a request action.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

    def authorize(self, identity, request_action):
        """
        Looks at the supplied identity object and returns True if the
        credentials are authorized to perform the requested action,
        False otherwise
        """
        return self.authfn(identity, request_action)
