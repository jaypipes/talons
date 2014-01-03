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

import binascii
import logging

import six

from talons import compat
from talons.auth import interfaces

LOG = logging.getLogger(__name__)


class Identifier(interfaces.Identifies):

    """
    Looks in HTTP Basic Access authentication headers and stores identity
    in the request environ's 'wsgi.identity' key. If no identity information
    is found, sets this key to None.

    Basic access authentication uses a client-sent HTTP "Authorize" header,
    with the string "Basic" and a base-64-encoded username:password string.

    :see http://en.wikipedia.org/wiki/Basic_access_authentication
    """

    def identify(self, request):
        if request.env.get(self.IDENTITY_ENV_KEY) is not None:
            return True

        http_auth = request.auth

        if isinstance(http_auth, six.string_types):
            http_auth = http_auth.encode('ascii')
        try:
            auth_type, user_and_key = http_auth.split(six.b(' '), 1)
        except ValueError as err:
            msg = ("Basic authorize header value not properly formed. "
                   "Supplied header {0}. Got error: {1}")
            msg = msg.format(http_auth, str(err))
            LOG.debug(msg)
            return False

        if auth_type.lower() == six.b('basic'):
            try:
                user_and_key = user_and_key.strip()
                user_and_key = compat.decodebytes(user_and_key)
                user_id, key = user_and_key.split(six.b(':'), 1)
                identity = interfaces.Identity(compat.b2u(user_id),
                                               key=compat.b2u(key))
                request.env[self.IDENTITY_ENV_KEY] = identity
                return True
            except (binascii.Error, ValueError) as err:
                msg = ("Unable to determine user and pass/key encoding. "
                       "Got error: {0}").format(str(err))
                LOG.debug(msg)
        return False
