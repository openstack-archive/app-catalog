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

from oslo_context import context
import webob.dec


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
