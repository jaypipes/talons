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

import falcon
import mock
import testtools

from talons import auth
from talons import exc

from tests import base


class TestCreateMiddleware(base.TestCase):

    def test_wrong_args(self):
        i = mock.MagicMock(spec=auth.Identifies)
        a = mock.MagicMock(spec=auth.Authenticates)
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(None, None)
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(i, None)
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(None, a)
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(dict(i=i), None)
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(None, dict(a=a))
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(a, i)
        with testtools.ExpectedException(exc.BadConfiguration):
            auth.create_middleware(auth.Authenticates, auth.Identifies)

    def test_constructor_with_classes(self):
        conf = {
            'delay_401': True
        }
        m = auth.create_middleware(auth.Identifies, auth.Authenticates, **conf)
        self.assertTrue(isinstance(m, auth.Middleware))
        self.assertTrue(isinstance(m.identifiers[0], auth.Identifies))
        self.assertTrue(isinstance(m.authenticators[0], auth.Authenticates))


class TestMiddleware(base.TestCase):

    def test_delay_401(self):

        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.__setitem__ = mock.MagicMock()

        i = mock.MagicMock()
        i.identify.return_value = False

        a = mock.MagicMock()
        a.authenticate.return_value = False

        m = auth.Middleware([i], [a], delay_401=True)
        self.assertEquals(None, m(req, None, None))

        calls = [mock.call('wsgi.identified', False)]
        self.assertEquals(calls, req.env.__setitem__.call_args_list)

        a.reset_mock()
        i.reset_mock()
        req.reset_mock()

        i.identify.return_value = True
        a.authenticate.return_value = True
        
        m = auth.Middleware([i], [a], delay_401=True)
        self.assertEquals(None, m(req, None, None))

        calls = [mock.call('wsgi.identified', True),
                 mock.call('wsgi.authenticated', True)]
        self.assertEquals(calls, req.env.__setitem__.call_args_list)

        a.reset_mock()
        a.authenticate.return_value = False

        m = auth.Middleware([i], [a], delay_401=False)
        with testtools.ExpectedException(falcon.HTTPUnauthorized):
            m(req, None, None)

        i.reset_mock()
        i.identify.return_value = False

        m = auth.Middleware([i], [a], delay_401=False)
        with testtools.ExpectedException(falcon.HTTPUnauthorized):
            m(req, None, None)
