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
from flask import stream_with_context
import requests

from openstack_catalog.api import api
from openstack_catalog.api import cors_allow
from openstack_catalog import settings


HEADERS_ANONYMOUS = {
    "x-identity-status": "None",
}


@api.route('/v2/')
def index_v2():
    data = "db\n"
    resp = Response(data, status=200, mimetype='text/plain')
    cors_allow(resp)
    return resp


@api.route('/v2/<path:path>', methods=['GET', 'HEAD', 'OPTIONS', 'POST',
                                       'PUT', 'UPDATE', 'DELETE', 'PATCH'])
def glare(path):
    if not path.startswith('db'):
        return Response("Not found", status=404, mimetype='text/plain')
    url = settings.GLARE_URL + path[2:]
    query = "&".join(("%s=%s" % item) for item in request.args.items())
    if query:
        url += "?" + query
    headers = HEADERS_ANONYMOUS.copy()
    cookie = request.headers.get("cookie")
    if cookie:
        headers["cookie"] = cookie
    if request.method == "GET":
        resp = requests.request(request.method, url, headers=headers)
        return Response(stream_with_context(resp.iter_content()),
                        status=resp.status_code,
                        mimetype=resp.headers["content-type"])
    else:
        headers["content-type"] = request.headers.get("content-type")
        resp = requests.request(request.method, url, headers=headers,
                                data=request.stream)
        return Response(resp.text, status=resp.status_code,
                        mimetype=resp.headers["content-type"])
