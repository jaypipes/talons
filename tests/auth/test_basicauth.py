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
import fixtures
import mock
import testtools

from talons.auth import basicauth


class TestBasicauth(testtools.TestCase):

    def setUp(self):
        self.useFixture(fixtures.FakeLogger())
        super(TestBasicauth, self).setUp()

    def test_auth_required_decorator(self):

        class MyResource(object):

            @auth.auth_required
            def on_post(self, req, resp):
                resp.status = falcon.HTTP_201

            def on_get(self, req, resp):
                resp.status = falcon.HTTP_200

        req = mock.MagicMock()
        resp = fakes.ResponseMock()
        resource = MyResource()
        with mock.patch('procession.api.auth.authenticate',
                        return_value=False):
            with testtools.ExpectedException(falcon.HTTPUnauthorized):
                resource.on_post(req, resp)
            resource.on_get(req, resp)
            self.assertEquals(resp.status, falcon.HTTP_200)

        with mock.patch('procession.api.auth.authenticate',
                        return_value=True):
            resource.on_post(req, resp)
            self.assertEquals(resp.status, falcon.HTTP_201)

    def test_authentication(self):

        class FakeRequest(object):

            """
            Used in  testing, where we only care to examine
            the status and body attributes.
            """

            def __init__(self, headers=None):
                if headers:
                    self.headers = dict([(k.lower(), v) for (k, v)
                                        in headers.iteritems()])
                else:
                    self.headers = {}

            def get_header(self, header):
                return self.headers.get(header.lower())

        anon_ctx = fakes.AnonymousContextMock()
        auth_ctx = fakes.AuthenticatedContextMock()

        self.assertFalse(auth.authenticate(anon_ctx, FakeRequest()))
        self.assertTrue(auth.authenticate(auth_ctx, FakeRequest()))

        class ContextToAuthenticate(object):

            def __init__(self):
                self.authenticated = None
                self.user_id = None
                self.roles = []

        # No x-auth-identity header...
        ctx = ContextToAuthenticate()
        req = FakeRequest()
        result = auth.authenticate(ctx, req)
        self.assertFalse(result)

        # No x-auth-key header...
        headers = {
            'x-auth-identity': 'fake'
        }
        ctx = ContextToAuthenticate()
        req = FakeRequest(headers=headers)
        result = auth.authenticate(ctx, req)
        self.assertFalse(result)

        headers = {
            'x-auth-token': 'faketoken',
            'x-auth-identity': 'fakeidentity'
        }
        ctx = ContextToAuthenticate()
        req = FakeRequest(headers=headers)
        with mock.patch('procession.api.auth.is_valid_token') as mocked:
            mocked.return_value = True
            result = auth.authenticate(ctx, req)
            self.assertTrue(result)
            mocked.assert_called_with('faketoken', 'fakeidentity')
            mocked.reset()
            mocked.return_value = False
            result = auth.authenticate(ctx, req)
            self.assertFalse(result)

