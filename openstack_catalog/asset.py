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


class Asset(object):
    def __init__(self, asset_data):
        self.bare_data = asset_data
        self.type_name = asset_data['type_name']
        # self.type_version = asset_data.pop('type_version')

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
            'type_name': self.bare_data.get('type_name'),
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
