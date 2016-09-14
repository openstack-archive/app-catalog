# Copyright (c) 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Session middleware for glare.

This middleware is used to retrieve identification information about user
from memcached. This information should be stored there by app-catalog or
other compatible sofrware.

Session ID is taken from cookie and is matches the key in memcached database.
Data stored by this key is pickled dictionary with following keys:
  * launchpad_teams: comma separated names of launchpad teams
  * nickname: user name on launchpad

Sample filter configuration for glare-paste.ini:

  [filter:session]
  paste.filter_factory = \
          openstack_catalog.plugins.glare.middlewares:SessionMiddleware.factory
  memcached_server = 127.0.0.1:11211
  session_cookie_name = s.aoo
  trusted_hosts = 127.0.0.1

Option 'trusted_addresses' may be used for allowing some hosts to set identity
headers manually, e.g. for inial artifacts import.

"""

import memcache
import six
import webob.dec

import functools
import pickle

DEFAULT_MEMCACHED_SERVER = "127.0.0.1:11211"
DEFAULT_SESSION_COOKIE_NAME = "s.aoo"


class SessionMiddleware(object):

    def __init__(self, app, local_config):
        self.app = app
        self.client = memcache.Client(
            [local_config.get("memcached_server", DEFAULT_MEMCACHED_SERVER)])
        self._session_cookie_name = local_config.get(
            "session_cookie_name", DEFAULT_SESSION_COOKIE_NAME)
        self._trusted_addresses = local_config.get(
            "trusted_addresses", "").split(",")

    @classmethod
    def filter(cls, local_config, app):
        return cls(app, local_config)

    @classmethod
    def factory(cls, global_config, **local_config):
        return functools.partial(cls.filter, local_config)

    @webob.dec.wsgify
    def __call__(self, request):
        remote_addr = request.headers.get("REMOTE_ADDR")
        if remote_addr is not None and remote_addr not in self._trusted_hosts:
            request.headers["X-Identity-Status"] = "None"
        sid = request.cookies.get(self._session_cookie_name)
        if sid:
            session = self.client.get(sid)
            if session:
                try:
                    session = pickle.loads(six.b(session))
                except Exception:
                    session = False
                if session:
                    roles = ','.join(session["launchpad_teams"])
                    request.headers["X-Identity-Status"] = "Confirmed"
                    request.headers["X-Project-Id"] = session["nickname"]
                    request.headers["X-Roles"] = roles
        return request.get_response(self.app)
