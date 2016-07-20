# -*- coding: utf-8 -*-

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

from flask import Flask
from flask import Response

api = Flask('api')
api.debug = True


def cors_allow(resp):
    h = ['Origin',
         'Accept-Encoding',
         'Content-Type',
         'X-App-Catalog-Versions']
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = ', '.join(h)


@api.route('/')
def index():
    data = "v1\nv2\n"
    resp = Response(data, status=200, mimetype='plain/text')
    cors_allow(resp)
    return resp

# Pull in v1 api into the server.
from openstack_catalog.api.v1 import *  # noqa
from openstack_catalog.api.v2 import *  # noqa
