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

from flask import request
from flask import Response

from openstack_catalog.api import api
from openstack_catalog.api import cors_allow

from openstack_catalog import settings


@api.route('/v1')
def v1_index():
    data = "assets\nmurano_repo\n"
    resp = Response(data, status=200, mimetype='plain/text')
    cors_allow(resp)
    return resp


@api.route('/v1/assets', methods=['GET', 'OPTIONS'])
def assets_index():
    if request.method == 'OPTIONS':
        data = ''
    else:
        f = open(settings.ASSETS_FILE, 'r')
        data = f.read()
        f.close()
    resp = Response(data, status=200, mimetype='application/json')
    resp.headers['Access-Control-Max-Age'] = '3600'
    resp.headers['Cache-Control'] = 'max-age=3600'
    cors_allow(resp)
    return resp


@api.route('/v1/murano_repo/<release>/<path:path>')
def murano_repo_index(release, path):
    resp = Response('', status=302)
    resp.headers['Location'] = \
        "http://storage.apps.openstack.org/{}".format(path)
    return resp
