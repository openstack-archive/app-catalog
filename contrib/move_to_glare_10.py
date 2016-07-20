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

HEADERS_AUTH = {
    "x-identity-status": "Confirmed",
    "x-project-id": "app-catalog",
    "content-type": "application/json",
}
HEADERS_PATCH = HEADERS_AUTH.copy()
HEADERS_BLOB = HEADERS_AUTH.copy()
HEADERS_PATCH["content-type"] = "application/json-patch+json"
HEADERS_BLOB["content-type"] = "application/octet-stream"


def _get_keys(src, dst, *keys):
    for key in keys:
        if key in src:
            dst[key] = src[key]


class AssetUploader(object):

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
            if asset["name"] in self._assets:
                raise Exception("Duplicate name %s" % asset["name"])
            self._assets[asset["name"]] = asset

    def upload_assets(self):
        for name in self._assets:
            try:
                self.upload_asset(name)
            except Exception:
                logging.exception("Failed to create asset %s" % name)
                return
        for name, asset in self._assets.items():
            self._set_dependencies(asset)
        for asset_type, asset_id in self._uploaded.values():
            r = self._patch(asset_type, asset_id, [{
                "op": "replace",
                "path": "/status",
                "value": "active",
            }])
            if r.status_code != 200:
                logging.error("Failed to activate %s" % asset_id)

    def upload_asset(self, name):
        if name in self._uploaded:
            logging.debug("Already uploaded %s" % name)
            return
        asset = self._assets[name]
        artifact_type = asset["service"]["type"]
        method = getattr(self, "_process_%s" % artifact_type, None)
        if method:
            method(asset, self._get_common_data(asset))

    def _create_asset(self, artifact_type, data):
        logging.info("Creating %s '%s'" % (artifact_type, data["name"]))
        url = self._get_url("artifacts", artifact_type)
        r = requests.post(url, data=json.dumps(data), headers=HEADERS_AUTH)
        if r.status_code != 201:
            fmt = "Failed to create %s %s"
            raise Exception(fmt % (artifact_type, r.text))
        artifact = r.json()
        self._uploaded[data["name"]] = (artifact_type, artifact["id"])
        return artifact

    def _patch(self, artifact_type, asset_id, data):
        url = self._get_url("artifacts", artifact_type, asset_id)
        r = requests.patch(url, data=json.dumps(data),
                           headers=HEADERS_PATCH)
        return r

    def _activate_asset(self, artifact_type, asset_id):
        url = self._get_url("artifacts", artifact_type, asset_id)
        data = json.dumps([{
            "op": "replace",
            "path": "/status",
            "value": "active",
        }])
        logging.debug('Activating asset %s' % asset_id)
        r = requests.patch(url, data=data, headers=HEADERS_PATCH)
        if r.status_code != 200:
            logging.error(r.text)
            raise Exception("Failed to activate artifact %s" % asset_id)
        return r

    def _create_blob(self, asset_type, asset_id, blob_name, blob_url):
        asset_url = self._get_url("artifacts", asset_type, asset_id, blob_name)
        if self._download:
            data = requests.get(blob_url)
            r = requests.put(asset_url, data=data, headers=HEADERS_BLOB)
        else:
            data = {
                "external": True,
                "url": blob_url,
                "status": "active",
            }
            r = requests.put(asset_url, data=json.dumps(data),
                             headers=HEADERS_AUTH)
        logging.debug("Blob created %s" % r.status_code)
        return r

    def _get_common_data(self, asset):
        data = {}
        _get_keys(asset, data, "name", "description", "provided_by",
                  "release", "icon", "license", "license_url",
                  "supported_by")
        metadata = asset.get("attributes")
        if metadata:
            data["metadata"] = metadata
        return data

    def _set_dependencies(self, asset):
        depends = asset.get("depends")
        if depends:
            deps = []
            for item in depends:
                asset_type, asset_id = self._uploaded[item["name"]]
                deps.append("/artifacts/%s/%s" % self._uploaded[item["name"]])
            patch = [{
                "op": "replace",
                "path": "/depends",
                "value": deps,
            }]
            logging.debug("Setting deps for %s" % asset["name"])
            asset_id = self._uploaded[asset["name"]][1]
            logging.debug(patch)
            self._patch(asset_type, asset_id, patch)

    def _process_glance(self, asset, data):
        asset["attributes"].pop("size", None)
        _get_keys(asset["service"], data,
                  "min_disk", "min_ram", "disk_format",
                  "container_format", "image_indirect_url")
        image_url = asset["attributes"].pop("url", None)
        image = self._create_asset("glance_image", data)
        if image_url is None:
            return
        image_url = "http://127.0.0.1:8000"
        self._create_blob("glance_image", image["id"], "image", image_url)

    def _process_tosca(self, asset, data):
        url = asset["attributes"].pop("url")
        data["template_format"] = asset["service"]["template_format"]
        template = self._create_asset("tosca_template", data)
        self._create_blob("tosca_template", template["id"], "template", url)

    def _process_heat(self, asset, data):
        url = asset["attributes"].pop("url")
        _get_keys(asset, data, "environment", "template_version")
        template = self._create_asset("heat_template", data)
        self._create_blob("heat_template", template["id"], "template", url)

    def _process_murano(self, asset, data):
        url = asset["attributes"].pop("Package URL")
        data["package_name"] = asset["service"]["package_name"]
        package = self._create_asset("murano_package", data)
        self._create_blob("murano_package", package["id"], "package", url)

    def _process_bundle(self, asset, data):
        data["package_name"] = asset["service"]["murano_package_name"]
        self._create_asset("murano_package", data)


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
