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

from talons.auth import basicauth

from tests import base


@mock.patch('talons.auth.interfaces.Identity')
class TestBasicAuth(base.TestCase):

    def test_identity_already_exists(self, i_mock):
        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = ['something']

        i = basicauth.Identifier()
        i.identify(req)
        req.env.get.assert_called_once_with(i.IDENTITY_ENV_KEY)

    def test_bad_authenticate(self, i_mock):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="xxxx")
        type(req).auth = a_prop
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock(return_value=None)

        i = basicauth.Identifier()
        self.assertFalse(i.identify(req))
        a_prop.assert_called_once_with()
        self.assertFalse(i_mock.called)

    def test_non_basic_auth(self, i_mock):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="notbasic xxx")
        type(req).auth = a_prop
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock(return_value=None)

        i = basicauth.Identifier()
        self.assertFalse(i.identify(req))
        a_prop.assert_called_once_with()
        self.assertFalse(i_mock.called)

    def test_httpauth_none(self, i_mock):
        # Issue #29 showed incorrect behaviour when
        # falcon.request.Request.auth was None instead of the expected
        # auth_type, user_and_key tuple. Ensure we handle None.
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value=None)
        type(req).auth = a_prop
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock(return_value=None)

        i = basicauth.Identifier()
        self.assertFalse(i.identify(req))
        a_prop.assert_called_once_with()
        self.assertFalse(i_mock.called)

    def test_basic_invalid(self, i_mock):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="basic xxx")
        type(req).auth = a_prop
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock(return_value=None)

        i = basicauth.Identifier()
        self.assertFalse(i.identify(req))
        a_prop.assert_called_once_with()
        self.assertFalse(i_mock.called)

    def test_basic_valid(self, i_mock):
        req = mock.MagicMock()
        # Aladdin with key 'open sesame'
        valid_auth = "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
        a_prop = mock.PropertyMock(return_value=valid_auth)
        type(req).auth = a_prop
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock(return_value=None)

        i = basicauth.Identifier()
        self.assertTrue(i.identify(req))
        i_mock.assert_called_once_with(u'Aladdin', key=u'open sesame')
