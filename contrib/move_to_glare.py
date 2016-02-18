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

import argparse
import json
import requests
import sys
import tempfile
import yaml

parser = argparse.ArgumentParser(description='move assets into glare.')
parser.add_argument('--glare_url', metavar='g', type=str,
                    help='glare_url', default='http://127.0.0.1:9494/')
parser.add_argument('--assets_file', metavar='f', type=str,
                    help='assets_file',
                    default='openstack_catalog/web/api/v1/assets')
parser.add_argument('--download', action='store_true',
                    dest='download', help='download')
parser.set_defaults(download=False)

args = parser.parse_args()


def artifact_factory(asset_data):
    if (not asset_data.get('license', None) or
            not asset_data.get('provided_by', None)):
        raise Exception("Some required properties are not specified")

    type_name = asset_data['service'].get('type', None)
    asset_data['type_version'] = 1.0

    if type_name is None:
        raise Exception("Type is not specified")
    elif type_name == 'glance':
        asset_data['type_name'] = 'glance_images'
        return GlanceAsset(asset_data)

    elif type_name == 'bundle':
        asset_data['type_name'] = 'bundles'
        return BundleAsset(asset_data)

    elif type_name == 'heat':
        asset_data['type_name'] = 'heat_templates'
        return HeatTemplateAsset(asset_data)

    elif type_name == 'murano':
        asset_data['type_name'] = 'murano_packages'
        return MuranoAsset(asset_data)

    elif type_name == 'tosca':
        asset_data['type_name'] = 'tosca_templates'
        return ToscaTemplateAsset(asset_data)


class ArtifactRepo(object):
    def __init__(self, glare_url):
        self.glare_url = glare_url

    def create(self, data, type_name, type_version):
        headers = {'Content-Type': 'application/json'}
        url = self.glare_url
        url += '/v0.1/artifacts/%s/v%s/drafts' % (type_name, type_version)
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        if not resp.ok:
            raise Exception(resp.content)
        return resp.json()

    def upload_blob(self, artifact_id, property_name, data,
                    type_name, type_version):
        headers = {'Content-Type': 'application/octet-stream'}
        url = self.glare_url
        url += '/v0.1/artifacts/%s/v%s/%s/%s' % (type_name, type_version,
                                                 artifact_id, property_name)
        resp = requests.put(url, data=data, headers=headers)
        if not resp.ok:
            raise Exception(resp.content)
        return resp

    def active(self, artifact_id, type_name, type_version):
        url = self.glare_url
        url += '/v0.1/artifacts/%s/v%s/%s/publish' % (type_name, type_version,
                                                      artifact_id)
        resp = requests.post(url)
        if not resp.ok:
            raise Exception(resp.content)
        return resp


class Asset(object):
    def __init__(self, asset_data):
        self.bare_data = asset_data
        self.type_name = asset_data.pop('type_name')
        self.type_version = asset_data.pop('type_version')

    def prepare_data(self):
        asset_draft = {
            'name': self.bare_data.get('name'),
            'version': self.bare_data.get('version', '0.0.0'),
            'provided_by': self.bare_data.get('provided_by'),
            'supported_by': self.bare_data.get('supported_by', None),
            'release': self.bare_data.get('release', ['Kilo']),
            'icon': self.bare_data.get('icon', None),
            'license': self.bare_data.get('license', None),
            'attributes': self.bare_data.get('attributes', None),
            'active': self.bare_data.get('active', True),
            'depends': self.bare_data.get('depends', []),
            'description': self.bare_data.get('description', ''),
            'tags': self.bare_data.get('tags', [])
        }
        if asset_draft['supported_by'] is None:
            asset_draft['supported_by'] = asset_draft['provided_by']

        asset_url = None
        if asset_draft['attributes'] is not None:
            attrs = asset_draft['attributes']
            asset_url = (attrs.get('url', None) or
                         attrs.get('Package URL', None))

            # convert attributes to dict of strings
            if asset_draft['attributes']:
                asset_draft['attributes'] = {
                    k: str(v) for k, v in asset_draft['attributes'].items()
                }

        if asset_url:
            if 'storage.apps.openstack' in asset_url and args.download:
                asset_draft['stored'] = True
                resp = requests.get(asset_url, stream=True)

                if resp.ok:
                    binary_obj = tempfile.NamedTemporaryFile(mode='w+b')
                    sys.stdout.write('Downloading binary data of asset {0}'
                                     '...\n'.format(asset_draft['name']))
                    for chunk in resp.iter_content(1024 * 1024):
                        binary_obj.write(chunk)
                    binary_obj.flush()
                    self.bare_data['binary'] = open(binary_obj.name, 'rb')
            else:
                asset_draft['remote_object_url'] = asset_url
                asset_draft['stored'] = False
                asset_draft['remote_object_hash'] = \
                    self.bare_data.get('hash', '')

        return asset_draft

    def import_to_glare(self, glare):
        draft = self.prepare_data()
        artifact = glare.create(draft, self.type_name, self.type_version)
        artifact_id = artifact['id']

        if self.bare_data.get('binary', None):
            glare.upload_blob(artifact_id,
                              'stored_object',
                              self.bare_data['binary'],
                              self.type_name,
                              self.type_version)
        if draft['active']:
            glare.active(artifact_id, self.type_name,
                         self.type_version)
        return artifact_id


class MuranoAsset(Asset):
    def prepare_data(self):
        draft = super(MuranoAsset, self).prepare_data()
        draft['fqn'] = self.bare_data['service']['package_name']
        # NOTE(ddovbii): it's weird, but looks like it's the only
        # way to get package type
        if 'Library' in draft['name']:
            draft['package_type'] = 'Library'
        else:
            draft['package_type'] = 'Application'
        return draft


class GlanceAsset(Asset):
    def prepare_data(self):
        draft = super(GlanceAsset, self).prepare_data()
        service_data = self.bare_data['service']
        img_draft = {
            'container_format': service_data.get('container_format'),
            'disk_format': service_data.get('disk_format'),
            'min_ram': service_data.get('min_ram', 0),
            'min_disk': service_data.get('min_disk', 0)
        }
        draft.update(img_draft)
        return draft


class BundleAsset(Asset):
    def prepare_data(self):
        draft = super(BundleAsset, self).prepare_data()
        service_data = self.bare_data['service']
        draft['murano_package_name'] = service_data.get('murano_package_name')
        return draft


class HeatTemplateAsset(Asset):
    def prepare_data(self):
        draft = super(HeatTemplateAsset, self).prepare_data()
        service_data = self.bare_data['service']
        draft['environment'] = service_data.get('environment', None)
        if draft['environment']:
            draft['environment'] = {
                k: str(v) for k, v in draft['environment'].items()}
        draft['template_version'] = service_data.get('template_version',
                                                     '2013-05-23')
        draft['template_format'] = service_data.get('format', 'HOT')
        return draft


class ToscaTemplateAsset(Asset):
    def prepare_data(self):
        draft = super(ToscaTemplateAsset, self).prepare_data()
        draft['template_format'] = self.bare_data['service']['template_format']
        draft['ever'] = self.bare_data['service'].get('ever', None)
        return draft


def main():
    glare_endpoint = args.glare_url
    created_artifacts = {}

    def create_artifact(asset, assets_list):
        dependencies = asset.get('depends', [])
        a_name = asset['name']

        if len(dependencies) > 0:
            depends_ids = []
            for d in dependencies:
                d_name = d['name']
                if d_name in created_artifacts:
                    depends_ids.append(created_artifacts[d_name])
                else:
                    dep_asset = next(
                        (i for i in assets_list if i['name'] == d_name), None)
                    if dep_asset is None:
                        sys.stdout.write('Asset {0} required by {1} is not '
                                         'found in assets list.\n'
                                         .format(d_name, a_name))
                        continue

                    dep_artifact = create_artifact(dep_asset, assets_list)
                    assets_list.remove(dep_asset)
                    depends_ids.append(dep_artifact)
            asset['depends'] = depends_ids
        asset_art = artifact_factory(asset)
        artifact_id = asset_art.import_to_glare(glare)
        created_artifacts[a_name] = artifact_id
        sys.stdout.write('The artifact for asset with '
                         'name {0} is created.\n'.format(a_name))
        return artifact_id

    glare = ArtifactRepo(glare_endpoint)
    src = yaml.load(open(args.assets_file, 'r'))

    assets = src['assets']
    uncreated_assets = []
    while len(assets) > 0:
        asset_data = assets.pop()
        try:
            asset_artifact = create_artifact(asset_data, assets)
            created_artifacts[asset_data['name']] = asset_artifact
        except Exception as e:
            uncreated_assets.append(asset_data)
            sys.stdout.write('Unable to create artifact '
                             'for asset with name {0}. Reason {1}\n'.
                             format(asset_data['name'], e.message))

if __name__ == "__main__":
    main()
