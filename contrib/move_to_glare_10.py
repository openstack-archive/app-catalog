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
import logging
import requests
import urlparse
import yaml

logging.basicConfig(level=logging.DEBUG)


class AssetUploader(object):
    _headers = {"content-type": "application/json", "x-tenant": "dummy"}
    _headers_patch = {"content-type": "application/json-patch+json",
                      "x-tenant": "dummy"}
    _headers_blob = {"content-type": "application/octet-stream",
                     "x-tenant": "dummy"}

    def __init__(self, glare_url, filename, download):
        self._filename = filename
        self._glare_url = glare_url
        self._download = download
        self._assets = {}
        self._uploaded = {}

    def _get_url(self, *args):
        return urlparse.urljoin(self._glare_url, "/".join(args))

    def parse(self):
        for asset in yaml.safe_load(open(self._filename))["assets"]:
            self._assets[asset["name"]] = asset

    def upload_assets(self):
        for name in self._assets:
            self.upload_asset(name)

    def upload_asset(self, name):
        asset = self._assets[name]
        artifact_type = asset["service"]["type"]
        method = getattr(self, "_process_%s" % artifact_type, None)
        if method:
            method(asset)

    def _create_asset(self, artifact_type, data):
        logging.info("Creating %s asset '%s'" % (artifact_type, data["name"]))
        data = json.dumps(data)
        url = self._get_url("artifacts", artifact_type)
        r = requests.post(url, data=data, headers=self._headers)
        if r.status_code != 201:
            raise Exception("Failed to create artifact %s" % r.text)
        return r.json()

    def _activate_asset(self, artifact_type, asset_id):
        url = self._get_url("artifacts", artifact_type, asset_id)
        data = json.dumps([{
            "op": "replace",
            "path": "/status",
            "value": "active",
        }])
        r = requests.patch(url, data=data, headers=self._headers_patch)
        if r.status_code != 200:
            raise Exception("Failed to activate artifact %s" % asset_id)
        return r

    def _create_blob(self, asset_type, asset_id, blob_name, blob_url):
        blob_url = "http://127.0.0.1:9494/"  # DELME
        asset_url = self._get_url("artifacts", asset_type, asset_id, blob_name)
        if self._download:
            data = requests.get(blob_url)
            r = requests.put(asset_url, data=data, headers=self._headers_blob)
        else:
            data = {
                "external": True,
                "url": blob_url,
                "status": "active",
            }
            r = requests.put(asset_url, data=json.dumps(data),
                             headers=self._headers)
        return r

    def _get_common_data(self, asset):
        data = {}
        for key in ("name", "description", "depends", "provided_by", "release",
                    "icon", "license", "license_url", "supported_by"):
            if key in asset:
                data[key] = asset[key]
        return data

    def _process_glance(self, asset):
        data = self._get_common_data(asset)
        for key in ("min_disk", "min_ram", "disk_format", "container_format",
                    "image_indirect_url"):
            data[key] = asset["service"].get(key)
        image = self._create_asset("glance_image", data)
        image_url = asset["attributes"].get("url")
        self._create_blob("glance_image", image["id"], "image", image_url)
        self._activate_asset("glance_image", image["id"])

    def _process_tosca(self, asset):
        data = self._get_common_data(asset)
        data["template_format"] = asset["service"]["template_format"]
        template = self._create_asset("tosca_template", data)
        self._create_blob("tosca_template", template["id"], "template",
                          asset["attributes"]["url"])
        self._activate_asset("tosca_template", template["id"])


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
