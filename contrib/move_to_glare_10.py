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
import yaml


class AssetUploader(object):

    def __init__(self, glare_url, filename, download):
        self._filename = filename
        self._glare_url = glare_url
        self._download = download
        self._assets = {}
        self._uploaded = {}

    def parse(self):
        for asset in yaml.safe_load(open(self._filename))["assets"]:
            self._assets[asset["name"]] = asset

    def upload_assets(self):
        for name in self._assets:
            self.upload_asset(name)

    def upload_asset(self, name):
        asset = self._assets[name]
        method = getattr(self, "_process_%s" % asset["service"]["type"], None)
        if method:
            return method(asset)

    def _create(self, artifact_type, data):
        data = json.dumps(data)
        headers = {"content-type": "application/json", "x-tenant": "dummy"}
        r = requests.post(self._glare_url + "artifacts/%s" % artifact_type,
                          data=data, headers=headers)
        return r.json()

    def _get_common_data(self, asset):
        data = {}
        for key in ("name", "description", "depends", "provided_by", "release",
                    "icon", "license", "license_url"):
            data[key] = asset.get(key)
        data["supported_by"] = asset.get("supported_by", data["provided_by"])
        return data

    def _process_glance(self, asset):
        data = self._get_common_data(asset)
        for key in ("min_disk", "min_ram", "disk_format", "container_format"):
            data[key] = asset["service"].get(key)
        image = self._create("glance_image", data)
        print image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='move assets into glare.')
    parser.add_argument('--glare_url', metavar='g', type=str,
                        help='glare_url', default='http://127.0.0.1:9494/')
    parser.add_argument('--assets_file', metavar='f', type=str,
                        help='assets_file',
                        default='openstack_catalog/web/static/assets.yaml')
    parser.add_argument('--download', action='store_true',
                        dest='download', help='download')
    parser.set_defaults(download=False)
    args = parser.parse_args()
    uploader = AssetUploader(args.glare_url, args.assets_file,
                             args.download)
    uploader.parse()
    uploader.upload_assets()
