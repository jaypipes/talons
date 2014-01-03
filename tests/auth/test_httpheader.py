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
import testtools

from talons import exc
from talons.auth import httpheader

from tests import base


class TestHttpHeader(base.TestCase):

    def test_missing_user_header(self):
        with testtools.ExpectedException(exc.BadConfiguration):
            conf = dict()
            httpheader.Identifier(**conf)

    def test_missing_key_header(self):
        with testtools.ExpectedException(exc.BadConfiguration):
            conf = dict(httpheader_user='x-user')
            httpheader.Identifier(**conf)

    def test_good_constructor(self):
        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key',
                    httpheader_tenant='x-tenant')
        i = httpheader.Identifier(**conf)
        self.assertEquals('x-user', i.user_header)
        self.assertEquals('x-key', i.key_header)
        # list() below is because Python 3.3 dict.keys() returns
        # an iterable view, not a list.
        self.assertEquals(['tenant'], list(i.attr_headers.keys()))
        self.assertEquals(['x-tenant'], list(i.attr_headers.values()))

    def test_blacklisted_attrs(self):
        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key',
                    httpheader___mro__='BADDIE')
        i = httpheader.Identifier(**conf)
        self.assertEquals('x-user', i.user_header)
        self.assertEquals('x-key', i.key_header)
        self.assertEquals({}, i.attr_headers)

    def test_identify_no_headers(self):
        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = [None]
        gh_mock = mock.MagicMock()
        gh_mock.side_effect = [None, None]
        req.get_header = gh_mock

        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key',
                    httpheader_tenant='x-tenant')
        i = httpheader.Identifier(**conf)
        i.identify(req)
        req.env.get.assert_called_once_with('wsgi.identity')
        expected = [mock.call('x-user'), mock.call('x-key')]
        self.assertEquals(expected, gh_mock.call_args_list)

    def test_identify_identity_already_exist(self):
        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = ['something']

        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key')
        i = httpheader.Identifier(**conf)
        i.identify(req)
        req.env.get.assert_called_once_with('wsgi.identity')

    def test_identify_missing_headers(self):
        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = [None]
        gh_mock = mock.MagicMock()
        gh_mock.side_effect = ['Aladdin', None]
        req.get_header = gh_mock

        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key',
                    httpheader_tenant='x-tenant')
        i = httpheader.Identifier(**conf)
        i.identify(req)
        req.env.get.assert_called_once_with('wsgi.identity')
        expected = [mock.call('x-user'), mock.call('x-key')]
        self.assertEquals(expected, gh_mock.call_args_list)

    def test_identify_valid_headers(self):
        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = [None]
        gh_mock = mock.MagicMock()
        gh_mock.side_effect = ['Aladdin', 'open sesame']
        req.get_header = gh_mock

        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key')
        i = httpheader.Identifier(**conf)
        i.identify(req)
        req.env.get.assert_called_once_with('wsgi.identity')
        expected = [mock.call('x-user'), mock.call('x-key')]
        self.assertEquals(expected, gh_mock.call_args_list)

        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.get = mock.MagicMock()
        req.env.get.side_effect = [None]
        gh_mock = mock.MagicMock()
        gh_mock.side_effect = ['Aladdin', 'open sesame', 'genie']
        req.get_header = gh_mock

        conf = dict(httpheader_user='x-user',
                    httpheader_key='x-key',
                    httpheader_tenant='x-tenant')
        i = httpheader.Identifier(**conf)
        i.identify(req)
        req.env.get.assert_called_once_with('wsgi.identity')
        expected = [mock.call('x-user'),
                    mock.call('x-key'),
                    mock.call('x-tenant')]
        self.assertEquals(expected, gh_mock.call_args_list)
