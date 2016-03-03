# Copyright (c) 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django import forms


ASSETS_TYPES = (
    ("glance", "glance"),
    ("heat", "heat"),
    ("murano", "murano"),
    ("bundle", "bundle"),
    ("tosca", "tosca"),
)


class CreateAssetForm(forms.Form):
    name = forms.CharField(label="Asset name", max_length=255,
                           required=True)
    type_name = forms.ChoiceField(label="Type", choices=ASSETS_TYPES,
                                  widget=forms.Select(attrs={
                                      'onchange': 'load_form()'
                                      }), required=True)
    provided_by = forms.CharField(label="Provided by", max_length=255,
                                  required=True)
    supported_by = forms.CharField(label="Supported by", max_length=255)
    release = forms.CharField(label="Release", max_length=255)
    icon = forms.CharField(label="Icon url", max_length=255)
    license = forms.CharField(label="License", max_length=255)
    depends = forms.CharField(label="Depends", max_length=255)
    descriprion = forms.CharField(label="Description", max_length=255)
    bin_file = forms.FileField(label="Binary File", max_length=255,
                               required=True)


class CreateGlanceAssetForm(CreateAssetForm):
    glance_field = forms.CharField(label="Glance Field", max_length=255)
    _CONTAINERS_TYPES = (
        ("ami", "ami"),
        ("ari", "ari"),
        ("aki", "aki"),
        ("bare", "bare"),
        ("ovf", "ovf"),
    )
    _DISKS_TYPES = (
        ("ami", "ami"),
        ("ari", "ari"),
        ("aki", "aki"),
        ("vhd", "vhd"),
        ("vdmk", "vmdk"),
        ("raw", "raw"),
        ("qcow2", "qcow2"),
        ("vdi", "vdi"),
        ("iso", "iso"),
    )

    container_format = forms.ChoiceField(label="Container Format",
                                         required=True,
                                         choices=_CONTAINERS_TYPES,
                                         initial=1)
    disk_format = forms.ChoiceField(label="Disk Format", required=True,
                                    choices=_DISKS_TYPES, initial=1)
    min_ram = forms.IntegerField(min_value=0, initial=0, required=False)
    min_disk = forms.IntegerField(min_value=0, initial=0, required=False)


class CreateHeatAssetForm(CreateAssetForm):
    heat_field = forms.CharField(label="Heat field", max_length=255)
    _TEMPLATES_TYPES = (
        ("2013-05-23", "2013-05-23"),
        ("2014-10-16", "2014-10-16"),
        ("2015-04-30", "2015-04-30"),
        ("2015-10-15", "2015-10-15"),
    )

    environment = forms.CharField(label="Environment", max_length=255,
                                  required=True)
    template_version = forms.ChoiceField(choices=_TEMPLATES_TYPES,
                                         required=True)


class CreateMuranoAssetForm(CreateAssetForm):
    murano_field = forms.CharField(label="Murano Field", max_length=255)


class CreateBundleAssetForm(CreateAssetForm):
    bundle_field = forms.CharField(label="Bundle Field", max_length=255)


class CreateToscaAssetForm(CreateAssetForm):
    tosca_field = forms.CharField(label="Tosca Field", max_length=255)
