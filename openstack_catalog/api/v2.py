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

import re

from flask import request as flask_request
from flask import Response
from flask import stream_with_context
import requests

from openstack_catalog.api import api
from openstack_catalog.api import cors_allow
from openstack_catalog import auth
from openstack_catalog import settings

RESTRICTED_URLS = (
    ('POST',
     re.compile(r'artifacts/glance_images/v1.0/[a-f\-\d]{36}/publish',
                re.IGNORECASE)),
)

@api.route('/v2/')
def index_v2():
    data = "db\n"
    resp = Response(data, status=200, mimetype='plain/text')
    cors_allow(resp)
    return resp


@api.route('/v2/db/<path:url>',
           methods=['GET', 'POST', 'UPDATE', 'PUT',
                    'DELETE', 'HEAD', 'OPTIONS'])
def v2_passthrough_with_url(url):
    for method, url_re in RESTRICTED_URLS:
        if flask_request.method == method:
            m = url_re.search(url)
            if m:
                auth_info = auth.get_auth_info(flask_request)
                if auth_info["admin"]:
                    break
                return Response("Unauthorized", status=401,
                                mimetype="text/plain")
    return v2_passthrough(url)


@api.route('/v2/db/', methods=['GET'])
def v2_passthrough_without_url():
    return v2_passthrough(None)


def v2_passthrough(url):
    if (url):
        glare_url = "{}/v0.1/{}".format(settings.GLARE_URI, url)
    else:
        glare_url = "{}/v0.1".format(settings.GLARE_URI)
    headers = {'Content-Type': flask_request.headers['Content-Type']}
    data = flask_request.data

    req = requests.request(flask_request.method, glare_url, headers=headers,
                           data=data, stream=True)
    resp = Response(
        stream_with_context(req.iter_content()),
        content_type=req.headers['content-type'],
        status=req.status_code)
    return resp
