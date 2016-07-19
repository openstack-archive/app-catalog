# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from flask import request
from flask import Response
import requests

from openstack_catalog.api import api
from openstack_catalog.api import cors_allow
from openstack_catalog import settings


GLARE_HEADERS = {'x-tenant': settings.GLARE_TENANT}
GLARE_METHODS = ['GET', 'POST', 'UPDATE', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']


@api.route('/v2/')
def index_v2():
    data = "db\n"
    resp = Response(data, status=200, mimetype='text/plain')
    cors_allow(resp)
    return resp


@api.route('/v2/<path:path>', methods=GLARE_METHODS)
def glare(path):
    if not path.startswith('db'):
        return Response("Not found", status=404, mimetype='text/plain')
    url = "%s/%s" % (settings.GLARE_URL, path[2:])
    resp = requests.request(request.method, url, headers=GLARE_HEADERS)
    return Response(resp.text, status=resp.status_code,
                    mimetype=resp.headers["content-type"])
