# -*- encoding: utf-8 -*-
#
# Copyright 2013-2014 Jay Pipes
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

from talons import exc
from talons.auth import middleware
from talons.auth import interfaces

from tests import base


class TestCreateMiddleware(base.TestCase):

    def test_wrong_args(self):
        i = mock.MagicMock(spec=interfaces.Identifies)
        a = mock.MagicMock(spec=interfaces.Authenticates)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(None, None)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(i, None)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(None, a)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(dict(i=i), None)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(None, dict(a=a))
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(a, i)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(interfaces.Authenticates,
                                         interfaces.Identifies)
        with testtools.ExpectedException(exc.BadConfiguration):
            middleware.create_middleware(interfaces.Identifies,
                                         interfaces.Authenticates,
                                         interfaces.Identifies)

    def test_constructor_with_classes(self):
        conf = {
            'delay_401': True
        }
        m = middleware.create_middleware(interfaces.Identifies,
                                         interfaces.Authenticates,
                                         interfaces.Authorizes,
                                         **conf)
        self.assertTrue(isinstance(m, middleware.Middleware))
        self.assertTrue(isinstance(m.identifiers[0], interfaces.Identifies))
        self.assertTrue(isinstance(m.authenticators[0],
                        interfaces.Authenticates))
        self.assertTrue(isinstance(m.authorizer, interfaces.Authorizes))


class TestMiddleware(base.TestCase):

    def test_call(self):

        req = mock.MagicMock()
        req.env = mock.MagicMock()
        req.env.__setitem__ = mock.MagicMock()
        meth_mock = mock.PropertyMock(return_value=mock.sentinel.method)
        type(req).method = meth_mock

        i = mock.MagicMock()
        i.identify.return_value = False

        a = mock.MagicMock()
        a.authenticate.return_value = False

        m = middleware.Middleware([i], [a], None, delay_401=True,
                                  delay_403=True, default_authorize=True)
        self.assertEquals(None, m(req, None, None))

        calls = [mock.call('wsgi.identified', False)]
        self.assertEquals(calls, req.env.__setitem__.call_args_list)

        a.reset_mock()
        i.reset_mock()
        req.reset_mock()

        i.identify.return_value = True
        a.authenticate.return_value = True

        m = middleware.Middleware([i], [a], None, delay_401=True,
                                  delay_403=True, default_authorize=True)
        self.assertEquals(None, m(req, None, None))

        calls = [mock.call('wsgi.identified', True),
                 mock.call('wsgi.authenticated', True),
                 mock.call('wsgi.authorized', True)]
        self.assertEquals(calls, req.env.__setitem__.call_args_list)

        req.reset_mock()

        m = middleware.Middleware([i], [a], None, delay_401=True,
                                  delay_403=True, default_authorize=False)
        self.assertEquals(None, m(req, None, None))

        calls = [mock.call('wsgi.identified', True),
                 mock.call('wsgi.authenticated', True),
                 mock.call('wsgi.authorized', False)]
        self.assertEquals(calls, req.env.__setitem__.call_args_list)

        a.reset_mock()
        a.authenticate.return_value = False

        m = middleware.Middleware([i], [a], None, delay_401=False)
        with testtools.ExpectedException(falcon.HTTPUnauthorized):
            m(req, None, None)

        i.reset_mock()
        i.identify.return_value = False
        req.reset_mock()

        m = middleware.Middleware([i], [a], delay_401=False)
        with testtools.ExpectedException(falcon.HTTPUnauthorized):
            m(req, None, None)

        a.reset_mock()
        i.reset_mock()
        req.reset_mock()

        z = mock.MagicMock()
        z.authorize.return_value = False

        i.identify.return_value = True
        a.authenticate.return_value = True

        res = self.patch('talons.auth.interfaces.ResourceAction')
        res.return_value = mock.sentinel.resource

        m = middleware.Middleware([i], [a], z, delay_401=True,
                                  delay_403=True, default_authorize=True)
        self.assertEquals(None, m(req, None, None))

        calls = [mock.call('wsgi.identified', True),
                 mock.call('wsgi.authenticated', True),
                 mock.call('wsgi.authorized', False)]
        self.assertEquals(calls, req.env.__setitem__.call_args_list)
        z.authorize.assert_called_once_with(mock.ANY, mock.sentinel.resource)

        a.reset_mock()
        i.reset_mock()
        z.reset_mock()
        req.reset_mock()

        i.identify.return_value = True
        a.authenticate.return_value = True
        z.authorize.return_value = False

        m = middleware.Middleware([i], [a], z, delay_401=False,
                                  delay_403=False)
        with testtools.ExpectedException(falcon.HTTPForbidden):
            m(req, None, None)
