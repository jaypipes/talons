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


class Identifies(object):
    
    """
    Base class for plugins that act to identify the requesting user,
    possibly by inspecting headers in the incoming HTTP request or
    looking in the wsgi.environ.
    """

    IDENTITY_ENV_KEY = 'wsgi.identity'

    def identify(self, request, response, params):
        """
        Looks and stores identity information in the request environ's
        'wsgi.identity' key. If not identity information is found, this
        key shall be set to None.
        """
        raise NotImplementedError
