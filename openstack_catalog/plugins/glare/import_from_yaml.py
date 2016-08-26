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
    "x-roles": "app-catalog-core",
    "content-type": "application/json",
}
HEADERS_PATCH = HEADERS_AUTH.copy()
HEADERS_PATCH["content-type"] = "application/json-patch+json"


def _get_keys(src, dst, *keys):
    for key in keys:
        if key in src:
            dst[key] = src[key]


class AssetUploader(object):

    def __init__(self, glare_url, filename):
        self._filename = filename
        self._glare_url = glare_url
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
            try:
                self._set_icon(asset)
            except Exception:
                logging.exception("Unable to create icon %s (%s, %s)" % (asset["name"], asset["provided_by"], asset.get("supported_by", "None")))
        for asset_type, asset in self._uploaded.values():
            r = self._patch(asset_type, asset["id"], [{
                "op": "replace",
                "path": "/status",
                "value": "active",
            }])
            if r.status_code != 200:
                logging.error("Failed to activate %s" % asset["id"])
            r = self._patch(asset_type, asset["id"], [{
                "op": "replace",
                "path": "/visibility",
                "value": "public",
            }])
            if r.status_code != 200:
                logging.error("Failed to publish %s" % asset["id"])

    def upload_asset(self, name):
        if name in self._uploaded:
            logging.debug("Already uploaded %s" % name)
            return
        asset = self._assets[name]
        artifact_type = asset["service"]["type"]
        method = getattr(self, "_process_%s" % artifact_type, None)
        if method:
            asset_data = self._get_common_data(asset)
            try:
                method(asset, asset_data)
            except Exception:
                logging.exception("Error creating asset '%s'" % name)

    def _create_asset(self, artifact_type, data):
        logging.info("Creating %s '%s'" % (artifact_type, data["name"]))
        url = self._get_url("artifacts", artifact_type)
        r = requests.post(url, data=json.dumps(data), headers=HEADERS_AUTH)
        if r.status_code != 201:
            logging.error("")
            fmt = "Failed to create %s %s"
            logging.error(fmt % (artifact_type, r.text))
            raise Exception("Failed to create '%s'" % data["name"])
        artifact = r.json()
        self._uploaded[data["name"]] = (artifact_type, artifact)
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

    def _create_blob(self, asset_type, asset_id, blob_name, blob_url,
                     download=True):
        asset_url = self._get_url("artifacts", asset_type, asset_id, blob_name)
        headers = HEADERS_AUTH.copy()
        if download:
            data = requests.get(blob_url, headers={"User-Agent": "Hello HyperGlance"})
            if data.status_code != 200:
                raise Exception("Failed to get %s" % blob_url)
            headers["content-type"] = data.headers.get(
                "content-type", "application/octet-stream")
        else:
            data = json.dumps({"url": blob_url})
            headers["content-type"] = "application/glare-external-location"
        r = requests.put(asset_url, data=data, headers=headers)
        if r.status_code == 200:
            logging.debug("Blob created %s" % r.status_code)
        else:
            logging.error("Failed to craete blob %s" % r.text)
        return r

    def _get_common_data(self, asset):
        data = {"metadata": {}}
        _get_keys(asset, data, "name", "description", "provided_by",
                  "release", "license", "license_url", "tags",
                  "supported_by")
        data["metadata"].update(asset.get("attributes", {}))
        for icon_key, icon_value in asset.pop("icon", {}).items():
            data["metadata"]["icon_" + icon_key] = icon_value
        if "supported_by" not in data:
            #remove this when glare get fixed
            data["supported_by"] = {"name": "Unknown"}
        return data

    def _set_dependencies(self, asset):
        logging.debug("getting deps from asset %s" % asset)
        depends = asset.get("depends")
        logging.debug("got %s" % depends)
        if depends:
            deps = []
            for item in depends:
                asset_type, asset = self._uploaded[item["name"]]
                deps.append("/artifacts/%s/%s" % (asset_type, asset["id"]))
            patch = [{
                "op": "replace",
                "path": "/depends",
                "value": deps,
            }]
            logging.debug("Setting deps for %s" % asset["name"])
            asset = self._uploaded[asset["name"]][1]
            logging.debug(patch)
            self._patch(asset_type, asset["id"], patch)

    def _set_icon(self, asset):
        asset_type, asset = self._uploaded[asset["name"]]
        logging.debug(asset)
        metadata = asset.get("metadata")
        if metadata:
            icon_url = metadata.get("icon_url")
            if icon_url:
                r = self._create_blob(asset_type, asset["id"], "icon", icon_url)
                logging.debug(repr(r))
                if r.status_code != 200:
                    logging.error("Unable to create icon: %s for artifact %s", icon_url, asset)

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
        self._create_blob("glance_image", image["id"],
                          "image", image_url, False)

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


def main():
    parser = argparse.ArgumentParser(description='move assets into glare.')
    parser.add_argument('--glare_url', metavar='g', type=str,
                        help='glare_url', default='http://127.0.0.1:9494/')
    parser.add_argument('--assets_file', metavar='f', type=str,
                        help='assets_file',
                        default='openstack_catalog/web/static/assets.yaml')
    args = parser.parse_args()
    uploader = AssetUploader(args.glare_url, args.assets_file)
    uploader.parse()
    uploader.upload_assets()
