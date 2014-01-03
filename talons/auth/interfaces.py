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
        credentials can be verified, False otherwise.
        """
        raise NotImplementedError  # pragma: NO COVER
