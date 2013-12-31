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

# The below is ripped from the _compat module in repoze.who.
# This probably should be in the six library...not quite sure why it isn't...
# https://github.com/repoze/repoze.who/blob/master/repoze/who/_compat.py

import base64

if 'decodebytes' in base64.__dict__:  # pragma NO COVER Python >= 3.0
    decodebytes = base64.decodebytes
    encodebytes = base64.encodebytes

    def decodestring(value):
        return base64.decodebytes(bytes(value, 'ascii')).decode('ascii')

    def encodestring(value):
        return base64.encodebytes(bytes(value, 'ascii')).decode('ascii')

else:  # pragma NO COVER Python < 3.0
    decodebytes = base64.decodestring
    encodebytes = base64.encodestring
    decodestring = base64.decodestring
    encodestring = base64.encodestring


def b2u(subject):
    if type(subject) is type(b''):
        try:
            return subject.decode('utf-8')
        except UnicodeDecodeError:
            return subject.decode('latin-1')
    return subject
