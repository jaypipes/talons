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

import testtools

from talons import helpers

from tests import base


class TestHelpers(base.TestCase):

    def test_bad_import(self):
        with testtools.ExpectedException(ImportError):
            helpers.import_function('not.exist.function')

    def test_no_function_in_module(self):
        with testtools.ExpectedException(ImportError):
            helpers.import_function('sys.noexisting')

    def test_not_callable(self):
        with testtools.ExpectedException(TypeError):
            helpers.import_function('sys.stdout')

    def test_return_function(self):
        fn = helpers.import_function('os.path.join')
        self.assertEqual(callable(fn), True)
