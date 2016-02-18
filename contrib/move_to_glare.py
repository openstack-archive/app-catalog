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

import requests
import tempfile
import yaml

def artifact_factory(asset_data):
    if not asset_data.licence or not asset_data.provided_by:
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


class ArtifactRepo(object):
    def __init__(self, glare_url):
        self.glare_url = glare_url

    def create(self, data, type_name, type_version):
        url = self.glare_url
        url += '/v0.1/artifacts/%s/v%s/drafts' % (type_name, type_version)
        resp = requests.post(url, data)
        return resp.json()

    def upload_blob(self, artifact_id, property_name, data,
                    type_name, type_version):
        headers = {'Content-Type': 'application/octet-stream'}
        url = self.glare_url
        url += '/v0.1/artifacts/%s/v%s/%s/%s' % (type_name, type_version,
                                              artifact_id, property_name)
        resp = requests.put(data=data, headers=headers)
        return resp

    def active(self, artifact_id, type_name, type_version):
        url = self.glare_url
        url += '/v0.1/artifacts/%s/v%s/%s/publish' % (type_name, type_version,
                                                      artifact_id)
        resp = requests.post(url)
        return resp

class Asset(object):
    def __init__(self, asset_data):
        self.bare_data = asset_data
        self.type_name = asset_data.pop('type_name')
        self.type_version = asset_data.pop('type_version')

    def prepare_data(self):
        asset_draft = {
            'provided_by': self.bare_data.get('provided_by'),
            'supported_by': self.bare_data.get('supported_by', None),
            'release': self.bare_data.get('release', []),
            'icon': self.bare_data.get('icon', None),
            'license': self.bare_data.get('license', None),
            'attributes': self.bare_data.get('attributes', None),
            'active': self.bare_data.get('active', True),
            'release': self.bare_data.get('depends', []),
        }

        asset_url = None
        if asset_draft['attributes'] is not None:
            attrs = asset_draft['attributes']
            asset_url = (attrs.get('url', None) or
                         attrs.get('Package URL', None))

        if asset_url:
            if 'storage.apps.openstack' in asset_url:
                asset_draft['stored'] = True

                resp = requests.get(asset_url, stream=True)
                if resp.ok:
                    binary_obj = tempfile.NamedTemporaryFile(mode='w+b')
                    for chunk in resp.iter_content(1024 * 1024):
                        binary_obj.write(chunk)
                    binary_obj.flush()
                    self.bare_data['binary'] = open(binary_obj.name, 'rb')
            else:
                asset_draft['remote_object_url'] = asset_url


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
        pkg_draft = {
            'fqn': self.data['service']['package_name'],
            # NOTE(ddovbii): How can we get package_type?
            # Looks like we need to open package's zip archive
            'package_type': self.data.get('package_type', 'Application')
        }
        draft.update(pkg_draft)
        return draft


class GlanceAsset():
    pass


class BundleAsset():
    pass


class HeatTemplateAsset():
    pass


def main():
    #TODO(ddovbii): Allow specifing from CLI
    glare_endpoint = 'http://127.0.0.1:9494/
    assets_url = 'https://raw.github.com/openstack/app-catalog' \
                 '/master/openstack_catalog/web/static/assets.yaml'
    created_artifacts = []

    glare = ArtifactRepo(glare_endpoint)
    r = requests.get(assets_url)
    src = yaml.load(r.text)

    for asset in src['assets']:
        asset_art = artifact_factory(asset)
        asset_art.import_to_glare(glare)

    def create_artifact(asset, assets_list):
        dependencies = asset.get('depends', [])
        if len(dependencies) > 0:
            depends_ids = []
            for d in dependencies:
                d_name = d['name']
                if d_name in created_artifacts:
                    depends_ids.append(created_artifacts[d_name])
                else:
                    dep_asset = next(i for i in assets_list
                                   if i['name'] == d_name)
                    dep_artifact = create_artifact(dep_asset, assets_list)
                    assets_list.remove(dep_asset)
                    depends_ids.append(dep_artifact)
            asset['depends'] = depends_ids
        else:
            asset_art = artifact_factory(asset)
            asset_id = asset_art.import_to_glare(glare)
            return asset_id


if __name__ == "__main__":
    main()
