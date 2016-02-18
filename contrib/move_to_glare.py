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
import yaml

def asset_factory(asset_data):
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
            'active': self.bare_data.get('active', True)
        }
        return asset_draft

    def import_to_glare(self, glare):
        draft = self.prepare_data()
        artifact = glare.create(draft, self.type_name, self.type_version)
        artifact_id = artifact['id']
        setattr(self, 'id', artifact_id)
        if draft['active']:
            glare.active()
        #TODO(ddovbii): Upload binary data to Glare


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

    glare = ArtifactRepo(glare_endpoint)
    r = requests.get(assets_url)
    src = yaml.load(r.text)

    for asset in src['assets']:
        asset_art = asset_factory(asset)
        asset_art.import_to_glare(glare)

if __name__ == "__main__":
    main()
