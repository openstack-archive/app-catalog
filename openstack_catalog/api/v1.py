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

import json
from flask import request
from flask import Response
import requests

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
    data = get_assets_from_glare()
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


def get_assets_from_glare():
    assets = []
    for artifact_type, process_asset in (
        ('tosca_template', _process_tosca_asset),
        ('murano_package', _process_murano_asset),
        ('heat_template', _process_heat_asset),
        #('glance_image', _process_glance_asset),
        ):
        url = settings.GLARE_URL + '/artifacts/' + artifact_type
        for artifact in  requests.get(url).json()[artifact_type]:
            asset = {}
            _copy_keys(artifact, asset, ('name', 'provided_by', 'supported_by',
                                         'tags', 'description', 'license',
                                         'license_url', 'metadata'))
            process_asset(artifact, asset)
            assets.append(asset)
        #TODO dependencies, hash
    return json.dumps({"assets": assets})


def _copy_keys(src, dst, keys):
    for key in keys:
        value = src.get(key)
        if value is not None:
            dst[key] = value


def _blob_url(blob_type, blob_id, blob_name):
    return '%s/artifacts/%s/%s/%s' % (settings.PUBLIC_GLARE_URL,
                                      blob_type, blob_id, blob_name)


def _process_tosca_asset(src, dst):
    dst['service'] = {'type': 'tosca', 'template_format': src['template_format']}
    dst['attributes'] = {'url': _blob_url('tosca_template', src['id'], 'template')}


def _process_murano_asset(src, dst):
    package_format = 'package' if src['package'] else 'bundle'
    dst['service'] = {'type': 'murano', 'format': package_format,
                      'package_name': src['package_name']}
    package_url = _blob_url('murano_package', src['id'], 'package')
    dst['attributes'] = {'Package URL': package_url}
    source_url = src['metadata'].get("Source URL")
    if source_url:
        dst['attributes']['Source URL'] = source_url

def _process_heat_asset(src, dst):
    dst['service'] = {'type': 'heat'}


def _process_glance_asset(src, dst):
    pass
