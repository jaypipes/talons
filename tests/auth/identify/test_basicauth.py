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

import mock

from talons.auth.identify import basicauth

from tests import base


class TestBasicAuth(base.TestCase):

    def test_non_basic_auth(self):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="notbasic xxx")
        type(req).auth = a_prop
        e_prop = mock.PropertyMock(return_value=dict())
        type(req).env = e_prop

        i = basicauth.BasicAuthIdentifier()
        i.identify(req)
        e_prop.assert_called_once_with()
        a_prop.assert_called_once_with()
