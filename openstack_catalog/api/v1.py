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

from flask import jsonify
from flask import request
from flask import Response
import json
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
        if settings.ASSETS_USE_GLARE:
            data = fetch_data_from_glare()
        else:
            with open(settings.ASSETS_FILE, 'r') as f:
                data = json.load(f)
    resp = jsonify(**data)
    # resp.headers['Access-Control-Max-Age'] = '3600'
    # resp.headers['Cache-Control'] = 'max-age=3600'
    cors_allow(resp)
    return resp


@api.route('/v1/murano_repo/<release>/<path:path>')
def murano_repo_index(release, path):
    resp = Response('', status=302)
    resp.headers['Location'] = \
        "http://storage.apps.openstack.org/{}".format(path)
    return resp


def fetch_data_from_glare():
    assets = []
    art_types = [
        'bundles',
        'glance_images',
        'heat_templates',
        'murano_packages',
        'tosca_templates',
    ]

    # TODO(kzaitsev): fetch these from glare itself and cache
    url_tmpl = "{glare_endpoint}/v0.1/artifacts/{art_type}/v1.0"
    for art in art_types:
        url = url_tmpl.format(glare_endpoint=settings.GLARE_URI,
                              art_type=art)
        resp = requests.get(url)
        if art == 'heat_templates':
            import pprint
            pprint.pprint(resp.json())
        if not resp.ok:
            continue

        data = resp.json()
        assets.extend([_adopt_for_v1(art) for art in data['artifacts']])

    return {'assets': assets}


def _adopt_for_v1(asset):
    asset.setdefault('service', {})
    if asset['type_name'] == 'BundleAsset':
        asset['service']['type'] = 'bundle'
        # TODO(kzaitsev): add bundle short name?
        asset['service']['murano_package_name'] = 'bundle_short_name'
    elif asset['type_name'] == 'GlanceImageAsset':
        asset['service']['type'] = 'glance'
        asset['service']['disk_format'] = asset['disk_format']
        asset['service']['container_format'] = asset['container_format']
        asset['service']['min_disk'] = asset['min_disk']
        asset['service']['min_ram'] = asset['min_ram']
    elif asset['type_name'] == 'MuranoPackageAsset':
        asset['service']['type'] = 'murano'
        asset['service']['package_name'] = asset['fqn']
        asset['service']['format'] = 'package'
    elif asset['type_name'] == 'HeatTemplateAsset':
        asset['service']['type'] = 'heat'
        # TODO(kzaitsev): we probably forgot this field in plugin scheme
        asset['service']['format'] = 'HOT'
    return asset
