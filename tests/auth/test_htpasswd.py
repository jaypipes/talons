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
from talons.auth import htpasswd

from tests import base


class TestExternal(base.TestCase):

    def test_missing_path(self):
        with testtools.ExpectedException(exc.BadConfiguration):
            conf = dict()
            htpasswd.Authenticator(**conf)

    def test_non_existing_path(self):
        with mock.patch('os.path.exists') as mocked:
            mocked.return_value = False
            with testtools.ExpectedException(exc.BadConfiguration):
                conf = dict(htpasswd_path='this.not.exist')
                htpasswd.Authenticator(**conf)

    def test_authfn_called(self):
        with mock.patch('os.path.exists') as ope_mock:
            ope_mock.return_value = True
            with mock.patch('passlib.apache.HtpasswdFile') as htf_mock:
                conf = dict(htpasswd_path='foo')
                auth = htpasswd.Authenticator(**conf)
                id_mock = mock.MagicMock()
                id_mock.login = 'foo'
                id_mock.key = 'bar'
                chk_mock = mock.MagicMock()
                htf = htf_mock.return_value
                htf.check_password = chk_mock
                auth.authenticate(id_mock)
                chk_mock.assert_called_once_with('foo', 'bar')
