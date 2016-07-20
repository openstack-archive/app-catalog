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

import memcache
from oslo_context import context
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

    @classmethod
    def filter(cls, local_config, app):
        return cls(app, local_config)

    @classmethod
    def factory(cls, global_config, **local_config):
        return functools.partial(cls.filter, local_config)

    @webob.dec.wsgify
    def __call__(self, request):
        remote_addr = request.headers.get("REMOTE_ADDR")
        if remote_addr is not None and remote_addr != "127.0.0.1":
            request.headers["X-Identity-Status"] = "None"
        sid = request.cookies.get(self._session_cookie_name)
        if sid:
            session = self.client.get(sid)
            if session:
                try:
                    session = pickle.loads(six.b(session))
                except Exception as ex:
                    session = False
                if session:
                    roles = ','.join(session["launchpad_teams"])
                    request.headers["X-Identity-Status"] = "Confirmed"
                    request.headers["X-Project-Id"] = session["nickname"]
                    request.headers["X-Roles"] = roles
        return request.get_response(self.app)


class UnsafeMiddleware(object):

    def __init__(self, app):
        self.app = app

    @classmethod
    def filter(cls, app):
        return cls(app)

    @classmethod
    def factory(cls, global_config, **local_config):
        return cls.filter

    @webob.dec.wsgify
    def __call__(self, request):
        tenant = None
        if request.remote_addr in ('127.0.0.1', '::1'):
            tenant = request.headers.get("x-tenant")
        request.context = context.RequestContext(tenant=tenant)
        return request.get_response(self.app)
