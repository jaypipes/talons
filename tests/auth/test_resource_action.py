# -*- encoding: utf-8 -*-
#
# Copyright 2014 Jay Pipes
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

from falcon import api
from falcon import testing as ftesting

from talons.auth import interfaces

from tests import base


class AppResource(object):

    def on_get(self, req, resp, user_id, **kwargs):
        resp.status = 200
        resp.body = user_id


class TestResource(base.TestCase):

    def setUp(self):
        self.resp_mock = ftesting.StartResponseMock()
        super(TestResource, self).setUp()

    def make_request(self, path, **kwargs):
        return self.app(ftesting.create_environ(path=path, **kwargs),
                        self.resp_mock)

    def test_dotted_notation(self):

        def hook(req, resp, params):
            self.res = interfaces.ResourceAction(req, params)
            hook.called = True

        hook.called = False

        app = api.API(before=[hook])
        app.add_route("/users/{user_id}", AppResource())
        self.app = app

        self.make_request('/users/123', method='GET')
        self.assertTrue(hook.called)
        res_dotted = self.res.to_string()
        self.assertEquals('users.123.get', res_dotted)

        hook.called = False

        self.make_request('/users/123?q=23491', method='GET')
        self.assertTrue(hook.called)
        res_dotted = self.res.to_string()
        self.assertEquals('users.123.get', res_dotted)
