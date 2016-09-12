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
    artifact_dependency_map = {}
    for artifact_type, process_asset in (
        ('tosca_templates', _process_tosca_asset),
        ('murano_packages', _process_murano_asset),
        ('heat_templates', _process_heat_asset),
        ('images', _process_image_asset),
        ):
        for artifact in _generate_artifacts(artifact_type):
            key = '/artifacts/%s/%s' % (artifact_type, artifact['id'])
            artifact_dependency_map[key] = artifact['name']
            asset = {}
            _copy_keys(artifact, asset, ('name', 'provided_by', 'supported_by',
                                         'tags', 'description', 'license',
                                         'license_url', 'dependencies'))
            _add_icon(artifact, asset, artifact_type)
            process_asset(artifact, asset)
            assets.append(asset)
    for asset in assets:
        deps = []
        for dependency in asset.get('dependencies', []):
            deps.append({'name': artifact_dependency_map[dependency]})
        if deps:
            asset['depends'] = deps
        asset.pop('dependencies', None)
    return json.dumps({"assets": assets})


def _generate_artifacts(artifact_type):
    url = settings.GLARE_URL + '/artifacts/' + artifact_type
    while True:
        response = requests.get(url).json()
        for artifact in response[artifact_type]:
            yield artifact
        next_page = response.get('next')
        if next_page:
            url = settings.GLARE_URL + next_page
        else:
            raise StopIteration


def _copy_keys(src, dst, keys):
    for key in keys:
        _copy_key(src, dst, key)


def _copy_key(src, dst, key):
    if key in src:
        dst[key] = src[key]


def _add_icon(src, dst, asset_type):
    if src['icon'] is None:
        return
    icon = {'url': _blob_url(asset_type, src['id'], 'icon')}
    for key in ('icon_top', 'icon_left', 'icon_height'):
        value = src['metadata'].get(key)
        if value:
            icon[key.split('_')[1]] = int(value)
    dst['icon'] = icon


def _blob_url(blob_type, blob_id, blob_name):
    return '%s/artifacts/%s/%s/%s' % (settings.PUBLIC_GLARE_URL,
                                      blob_type, blob_id, blob_name)


def _process_tosca_asset(src, dst):
    dst['service'] = {'type': 'tosca',
                      'template_format': src['template_format']}
    dst['attributes'] = {'url': _blob_url('tosca_templates', src['id'],
                                          'template')}


def _process_murano_asset(src, dst):
    package_format = 'package' if src['package'] else 'bundle'
    dst['service'] = {'type': 'murano', 'format': package_format,
                      'package_name': src['display_name']}
    if src['package'] is None:
        dst['service']['type'] = 'bundle'
    else:
        checksum = src['package'].get('checksum')
        if checksum:
            dst['hash'] = checksum
        package_url = _blob_url('murano_packages', src['id'], 'package')
        dst['attributes'] = {'Package URL': package_url}
        _copy_key(src['metadata'], dst['attributes'], 'Source URL')


def _process_heat_asset(src, dst):
    dst['service'] = {'type': 'heat', 'format': 'HOT'}
    dst['attributes'] = {'url': src['template']['url']}


def _process_image_asset(src, dst):
    dst['service'] = {
        'type': 'glance',
        'min_disk': src['min_disk'],
        'min_ram': src['min_ram'],
        'disk_format': src['disk_format'],
        'container_format': src['container_format'],
    }
    dst['attributes'] = {}
    if src['cloud_user'] is not None:
        dst['cloud_user'] = src['cloud_user']
    image = src.get('image')
    if image:
        dst['attributes']['url'] = _blob_url('images',
                                             src['id'], 'image')
        checksum = image.get('checksum')
        if checksum:
            dst['hash'] = checksum
    image_indirect_url = src.get('image_indirect_url')
    if image_indirect_url:
        dst['attributes']['image_indirect_url'] = image_indirect_url
