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

from assets.common import AssetArtifact

from glance.common.glare import definitions


class GlanceImageAsset(AssetArtifact):
    __endpoint__ = 'glance_images'

    container_format = definitions.String(mutable=False, required=True,
                                          allowed_values=[
                                              "ami", "ari", "aki", "bare",
                                              "ovf"])
    disk_format = definitions.String(mutable=False, required=True,
                                     allowed_values=[
                                         "ami", "ari", "aki", "vhd", "vmdk",
                                         "raw", "qcow2", "vdi", "iso"])
    min_ram = definitions.Integer(mutable=False, min_value=0, default=0)
    min_disk = definitions.Integer(mutable=False, min_value=0, default=0)
