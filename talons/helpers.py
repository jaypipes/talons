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

import logging
import sys
import traceback

LOG = logging.getLogger(__name__)


def import_function(import_str):
    """
    Attempts to import the specified class method or regular function,
    and returns a callable.

    :raises ImportError if the specified import_str cannot be found.
    :raises TypeError if the specified import_str is found but is
            not a callable.
    """
    mod_str, _sep, class_str = import_str.rpartition('.')
    try:
        __import__(mod_str)
        fn = getattr(sys.modules[mod_str], class_str)
        if not callable(fn):
            msg = '{0} is not callable'
            LOG.error(msg)
            raise TypeError(msg)
    except (ValueError, AttributeError):
        msg = 'Method or function {0} cannot be found.'.format(import_str)
        err_details = traceback.format_exception(*sys.exc_info())
        LOG.error(msg + ' Details: (%s)'.format(err_details))
        raise ImportError(msg)
    except ImportError:
        msg = 'Module {0} cannot be found.'.format(import_str)
        err_details = traceback.format_exception(*sys.exc_info())
        LOG.error(msg + ' Details: (%s)'.format(err_details))
        raise
    return fn
