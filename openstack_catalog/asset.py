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

import tempfile


def asset_factory(asset_data):
    type_name = asset_data.get('type_name', None)

    if type_name is None:
        raise Exception("Type is not specified")
    elif type_name == 'glance':
        return GlanceAsset(asset_data)

    elif type_name == 'bundle':
        return BundleAsset(asset_data)

    elif type_name == 'heat':
        return HeatTemplateAsset(asset_data)

    elif type_name == 'murano':
        return MuranoAsset(asset_data)

    elif type_name == 'tosca':
        return ToscaTemplateAsset(asset_data)


class Asset(object):
    def __init__(self, asset_data):
        self.bare_data = asset_data
        self.type_name = asset_data['type_name']
        self.type_version = 1.0

    def build_dict_by_prefix(self, prefix):
        d = {key: self.bare_data[key] for key in self.bare_data
             if key.startswith(prefix)}
        return d if d else None

    def build_array(self, key, sep=' '):
        a = self.bare_data.get(key, '').split(sep)
        return a

    def prepare_data(self):
        asset_draft = {
            'name': self.bare_data.get('name'),
            'version': self.bare_data.get('version', '0.0.0'),
            'provided_by': self.build_dict_by_prefix('provided_by'),
            'supported_by': self.build_dict_by_prefix('supported_by'),
            'release': self.bare_data.get('release', ['Kilo']),
            'icon': self.build_dict_by_prefix('icon'),
            'license': self.build_dict_by_prefix('license'),
            'active': self.bare_data.get('active', True),
            'depends': self.build_array('depends'),
            'description': self.bare_data.get('description', ''),
            'tags': self.build_array('tags'),
            # 'object': self.bare_data.get('asset_object', None),
        }

        obj = self.bare_data.get('asset_object', None)
        if obj:
            binary_obj = tempfile.NamedTemporaryFile(mode='w+b')
            for chunk in obj.chunks():
                binary_obj.write(chunk)
            binary_obj.flush()
            self.bare_data['binary'] = open(binary_obj.name, 'rb')
        else:
            self.bare_data['binary'] = None

        return asset_draft


class MuranoAsset(Asset):
    def prepare_data(self):
        draft = super(MuranoAsset, self).prepare_data()
        draft['type_name'] = 'murano_packages'
        draft['fqn'] = self.bare_data.get('fqn', '')
        draft['package_type'] = self.bare_data.get('package_type', '')
        return draft


class GlanceAsset(Asset):
    def prepare_data(self):
        draft = super(GlanceAsset, self).prepare_data()
        draft['type_name'] = 'glance_images'
        img_draft = {
            'container_format': self.bare_data.get('container_format', ''),
            'disk_format': self.bare_data.get('disk_format', ''),
            'min_ram': self.bare_data.get('min_ram', 0),
            'min_disk': self.bare_data.get('min_disk', 0)
        }
        draft.update(img_draft)
        return draft


class BundleAsset(Asset):
    def prepare_data(self):
        draft = super(BundleAsset, self).prepare_data()
        draft['type_name'] = 'bundles'
        return draft


class HeatTemplateAsset(Asset):
    def prepare_data(self):
        draft = super(HeatTemplateAsset, self).prepare_data()
        draft['type_name'] = 'heat_templates'
        draft['environment'] = self.bare_data.get('environment', None)
        draft['template_version'] = self.bare__data.get('template_version',
                                                        '2013-05-23')
        return draft


class ToscaTemplateAsset(Asset):
    def prepare_data(self):
        draft = super(ToscaTemplateAsset, self).prepare_data()
        draft['type_name'] = 'tosca_templates'
        draft['template_format'] = self.bare_data.get('template_format', '')
        draft['ever'] = self.build_dict_by_prefix('ever')
        return draft
