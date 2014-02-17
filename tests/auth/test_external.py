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
from talons.auth import external

from tests import base


class TestExternal(base.TestCase):

    def test_missing_authfn(self):
        with testtools.ExpectedException(exc.BadConfiguration):
            conf = dict()
            external.Authenticator(**conf)

    def test_authfn_not_importable(self):
        with mock.patch('talons.helpers.import_function') as mocked:
            mocked.side_effect = ImportError
            with testtools.ExpectedException(exc.BadConfiguration):
                conf = dict(external_authfn='this.not.exist')
                external.Authenticator(**conf)

    def test_authfn_not_callable(self):
        with mock.patch('talons.helpers.import_function') as mocked:
            mocked.side_effect = TypeError
            with testtools.ExpectedException(exc.BadConfiguration):
                conf = dict(external_authfn='this.not.callable')
                external.Authenticator(**conf)

    def test_authfn_wrong_signature(self):
        def authme(two, args):
            pass
        with mock.patch('talons.helpers.import_function') as mocked:
            mocked.return_value = authme
            with testtools.ExpectedException(exc.BadConfiguration):
                conf = dict(external_authfn='authme')
                external.Authenticator(**conf)

    def test_authfn_called(self):
        def authme(identity):
            return identity

        with mock.patch('talons.helpers.import_function') as mocked:
            mocked.return_value = authme
            conf = dict(external_authfn='authme')
            auth = external.Authenticator(**conf)
            self.assertEquals('this', auth.authenticate('this'))
            self.assertFalse(auth.sets_roles())
            self.assertFalse(auth.sets_groups())
