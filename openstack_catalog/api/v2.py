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

import json
import random
import requests
import six

from flask import request
from flask import Response
from flask import stream_with_context
import memcache
from openstack_catalog.api import api
from openstack_catalog.api import cors_allow
from openstack_catalog import settings


HEADERS_ANONYMOUS = {
    "x-identity-status": "None",
    "connection": "close",
}
HOP_BY_HOP_HEADERS = {
    'Connection',
    'Keep-Alive',
    'Public',
    'Proxy-Authenticate',
    'Transfer-Encoding',
    'Upgrade',
}
RECENT_CACHE_KEY = '_recent_'
RECENT_CACHE_TIME = 1200

cache = memcache.Client([settings.MEMCACHED_SERVER])


@api.route('/v2/')
def index_v2():
    data = "db\n"
    resp = Response(data, status=200, mimetype='text/plain')
    cors_allow(resp)
    return resp


def copy_headers(requests_response, flask_response):
    for key, value in six.iteritems(requests_response.headers):
        if key not in HOP_BY_HOP_HEADERS:
            flask_response.headers[key] = value


@api.route('/v2/db/recent')
def recent():
    response = cache.get(RECENT_CACHE_KEY)
    if not response:
        assets = []
        for artifact_type in ('images', 'heat_templates',
                              'murano_packages'):
            url = '%s/artifacts/%s' % (settings.GLARE_URL, artifact_type)
            url = '%s?sort=updated_at&version=latest' % url
            for asset in requests.get(url).json()[artifact_type][:5]:
                assets.append({
                    'name': asset['name'],
                    'type': artifact_type,
                    'id': asset['id'],
                    'icon': asset['icon'] is not None,
                })
        random.shuffle(assets)
        response = json.dumps(assets[:5])
        cache.set(RECENT_CACHE_KEY, response, time=RECENT_CACHE_TIME)
    return Response(response, mimetype='application/json')


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
        resp = requests.request(request.method, url, headers=headers,
                                allow_redirects=False)
        response = Response(stream_with_context(resp.iter_content()),
                            status=resp.status_code,
                            mimetype=resp.headers["content-type"])
        copy_headers(resp, response)
        return response
    else:
        headers["content-type"] = request.headers.get("content-type")
        resp = requests.request(request.method, url, headers=headers,
                                data=request.stream, allow_redirects=False)
        return Response(resp.text, status=resp.status_code,
                        mimetype=resp.headers["content-type"])
