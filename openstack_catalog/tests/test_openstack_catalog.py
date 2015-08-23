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

"""
test_openstack_catalog
----------------------------------

Tests for `openstack_catalog` module.
"""

import functools
import jsonschema
import six
import testtools
import yaml


class TestOpenstack_catalog(testtools.TestCase):
    def setUp(self):
        super(TestOpenstack_catalog, self).setUp()

    def _read_raw_file(self, file_name):
        if six.PY3:
            opener = functools.partial(open, encoding='utf8')
        else:
            opener = open
        with opener(file_name, 'r') as content_file:
            return content_file.read()

    def _read_file(self, file_name):
        return yaml.load(self._read_raw_file(file_name))

    def _verify_by_schema(self, file_name, schema):
        data = self._read_file(file_name)
        schema = self._read_file(schema)
        names = {}
        for asset in data['assets']:
            name = asset['name']
            if name in names:
                self.fail("Duplicate asset name: %s" % name)
            names[name] = True
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            self.fail(e)

    def test_asset_schema_conformance(self):
        self._verify_by_schema(
            'openstack_catalog/web/static/assets.yaml',
            'openstack_catalog/web/static/assets.schema.yaml')
