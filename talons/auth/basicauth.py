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

import falcon
import six

from talons import compat
from talons.auth import base

LOG = logging.getLogger(__name__)


class BasicAuthIdentity(base.Identifies):

    def identify(self, request, response, params):
        """
        Looks in HTTP Basic Auth headers and stores identity information
        in the request environ's 'wsgi.identity' key. If no identity information
        is found, sets this key to None.
        """
        if request.env.get(self.IDENTITY_ENV_KEY) is not None:
            return None

        http_auth = request.auth

        if isinstance(authorization, six.string_types):
            http_auth = http_auth.encode('ascii')
        try:
            auth_type, user_and_key = http_auth.split(six.b(' '), 1)
        except ValueError:
            return None

        if auth_type.lower() == six.b('basic'):
            try:
                user_and_key = user_and_key.strip()
                user_and_key = compat.decodebytes(user_and_key)
                user_id, key = user_and_key.split(six.b(':'), 1)
                user_id = compat.must_decode(user_id)
                key = compat.must_decode(key)
            except (binascii.Error, ValueError), err:
                msg = ("Unable to determine user and pass/key encoding. "
                       "Got error: {0}").format(str(err))
                LOG.debug(msg)
                return None

            request.env[self.IDENTITY_ENV_KEY] = dict(user_id=user_id, key=key)
