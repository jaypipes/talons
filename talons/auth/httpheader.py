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

import logging

from talons import exc
from talons.auth import interfaces

LOG = logging.getLogger(__name__)


class Identifier(interfaces.Identifies):

    """
    Looks in HTTP headers and stores identity in the request environ's
    'wsgi.identity' key. If no identity information is found, sets this key to
    None.
    """

    def __init__(self, **conf):
        """
        Construct a concrete object with a set of keyword configuration
        options.

        :param **conf:

            httpheader_user: HTTP header to look for user/login
                             name (required)
            httpheader_key: HTTP header to look for password/key
                            (required)
            httpheader_$ATTRIBUTE: HTTP header that, if found, will
                                   be used to add $ATTRIBUTE to the
                                   Identity object stored in the WSGI
                                   pipeline. (optional)

        :raises `talons.exc.BadConfiguration` if configuration options
                are not valid or conflict with each other.
        """
        self.user_header = conf.pop('httpheader_user', None)
        if not self.user_header:
            msg = ("Missing required httpheader_user configuration "
                   "option.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        self.key_header = conf.pop('httpheader_key', None)
        if not self.key_header:
            msg = ("Missing required httpheader_key configuration "
                   "option.")
            LOG.error(msg)
            raise exc.BadConfiguration(msg)

        def _is_bad_attr(attr):
            if attr.startswith('__'):
                return True
            return False

        self.attr_headers = {}
        for k, v in conf.items():
            if k.startswith('httpheader_'):
                attr = k[11:]
                if _is_bad_attr(attr):
                    msg = ("Found blacklisted attr name {0} in "
                           "httpheader configuration. "
                           "Stripping.").format(attr)
                    LOG.warn(msg)
                    continue
                self.attr_headers[attr] = v

    def identify(self, request):
        if request.env.get(self.IDENTITY_ENV_KEY) is not None:
            return True

        user_id = request.get_header(self.user_header)
        key = request.get_header(self.key_header)
        if not user_id or not key:
            return False

        identity = interfaces.Identity(user_id, key=key)
        for attr, header in self.attr_headers.items():
            setattr(identity, attr, request.get_header(header))
        request.env[self.IDENTITY_ENV_KEY] = identity
        return True
