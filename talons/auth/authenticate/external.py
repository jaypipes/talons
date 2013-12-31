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

from talons import auth
from talons import exc
from talons import helpers

LOG = logging.getLogger(__name__)


class Authenticator(auth.Authenticates):

    """
    Authenticates the supplied Identity by calling out to an external
    authentication function.
    """

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf:

            authenticate_external_authfn: Dotted-notation module.class.method
                                          or module.function that will be used
                                          to authenticate. This function will
                                          accept as its only argument the
                                          `talons.auth.Identity` object.

        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        authfn = conf.pop('authenticate_external_authfn', None)
        if not authfn:
            msg = ("Missing required authenticate_external_authfn "
                   "configuration option.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        # Try import'ing the auth function to ensure that it exists
        try:
            self.authfn = helpers.import_function(authfn)
        except (TypeError, ImportError):
            msg = ("authenticate_external_authfn either could not be found "
                   "or was not callable.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        # Ensure that the auth function signature is what we expect
        spec = inspect.getargspec(self.authfn)
        if len(spec[0]) != 1:
            msg = ("authenticate_external_authfn has an invalid function "
                   "signature. The function must take only a single "
                   "parameter.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

    def authenticate(self, identity):
        """
        Looks at the supplied identity object and returns True if the
        credentials can be verified, False otherwise.
        """
        return self.authfn(identity)
