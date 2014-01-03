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


class TestBasicAuth(base.TestCase):

    def test_identity_already_exists(self):
        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = ['something']

        i = basicauth.Identifier()
        i.identify(req)
        req.env.get.assert_called_once_with('wsgi.identity')

    def test_bad_authenticate(self):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="xxxx")
        type(req).auth = a_prop
        e_prop = mock.PropertyMock(return_value=dict())
        type(req).env = e_prop

        i = basicauth.Identifier()
        i.identify(req)
        e_prop.assert_called_once_with()
        a_prop.assert_called_once_with()

    def test_non_basic_auth(self):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="notbasic xxx")
        type(req).auth = a_prop
        e_prop = mock.PropertyMock(return_value=dict())
        type(req).env = e_prop

        i = basicauth.Identifier()
        i.identify(req)
        e_prop.assert_called_once_with()
        a_prop.assert_called_once_with()

    def test_basic_invalid(self):
        req = mock.MagicMock()
        a_prop = mock.PropertyMock(return_value="basic xxx")
        type(req).auth = a_prop
        e_prop = mock.PropertyMock(return_value=dict())
        type(req).env = e_prop

        mod_cls = 'talons.auth.interfaces.Identity'
        with mock.patch(mod_cls) as i_mock:
            i = basicauth.Identifier()
            i.identify(req)
            e_prop.assert_called_once_with()
            a_prop.assert_called_once_with()
            i_mock.assert_not_called()

    def test_basic_valid(self):
        req = mock.MagicMock()
        # Aladdin with key 'open sesame'
        valid_auth = "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
        a_prop = mock.PropertyMock(return_value=valid_auth)
        type(req).auth = a_prop
        e_prop = mock.PropertyMock(return_value=dict())
        type(req).env = e_prop

        mod_cls = 'talons.auth.interfaces.Identity'
        with mock.patch(mod_cls) as i_mock:
            i = basicauth.Identifier()
            i.identify(req)
            i_mock.assert_called_once_with(u'Aladdin', key=u'open sesame')

    def test_basic_bytes(self):
        req = mock.MagicMock()
        # Aladdin with key 'open sesame'
        valid_auth = "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
        a_prop = mock.PropertyMock(return_value=valid_auth)
        type(req).auth = a_prop
        e_prop = mock.PropertyMock(return_value=dict())
        type(req).env = e_prop

        mod_cls = 'talons.auth.interfaces.Identity'
        with mock.patch(mod_cls) as i_mock:
            i = basicauth.Identifier()
            i.identify(req)
            i_mock.assert_called_once_with(u'Aladdin', key=u'open sesame')
