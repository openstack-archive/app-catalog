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

from django.core.exceptions import ValidationError

from django import forms


def double_tuple_elements(tup):
    # Return tuple of tuples, where the latter consists of the
    # duplicated elemts of the input tuple.
    # Pretty works to create choice field, where every element consists
    # of two equal strings.
    return tuple((t, t) for t in tup)


class CreateAssetForm(forms.Form):
    _ASSETS_CHOICES = double_tuple_elements(("glance", "heat", "murano",
                                             "bundle", "tosca"))
    _LICENSE_PATTERN = ("^(GPL .*)|(Apache .*)|(BSD .*)|(MIT)|"
                        "(Free <= [0-9]+ (Users|Nodes))|"
                        "(Multi-licensed OpenSource)|(Other)|(Unknown)$")

    _RELEASE_CHOICES = double_tuple_elements(('Austin', 'Bexar', 'Cactus',
                                              'Diablo', 'Essex', 'Folsom',
                                              'Grizzly', 'Havana', 'Icehouse',
                                              'Juno', 'Kilo', 'Liberty',
                                              'Mitaka', 'Newton', 'Ocata'))

    name = forms.CharField(max_length=256)
    type_name = forms.ChoiceField(choices=_ASSETS_CHOICES,
                                  widget=forms.Select(attrs={
                                      'onchange': 'load_form()'
                                      }))

    supported_by_name = forms.CharField(max_length=256)
    supported_by_mail = forms.EmailField()
    supported_by_company = forms.CharField(max_length=256, required=False)
    supported_by_irc_handle = forms.CharField(max_length=256, required=False)

    provided_by_name = forms.CharField(max_length=256)
    provided_by_mail = forms.EmailField()
    provided_by_company = forms.CharField(max_length=256, required=False)
    provided_by_irc_handle = forms.CharField(max_length=256, required=False)

    depends = forms.CharField(max_length=256, required=False)

    release = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        choices=_RELEASE_CHOICES)

    icon_top = forms.IntegerField()
    icon_left = forms.IntegerField()
    icon_height = forms.IntegerField()
    icon_url = forms.URLField()

    # license = forms.RegexField(regex=_LICENSE_PATTERN, max_length=2000)
    license_url = forms.URLField(required=False)

    # asset can be added only as a bin file
    asset_object = forms.FileField()

    active = forms.BooleanField(initial="True", required=False)
    description = forms.CharField(max_length=2000, required=False)
    tags = forms.CharField(max_length=256, required=False)


class CreateGlanceAssetForm(CreateAssetForm):
    _CONTAINERS_CHOICES = double_tuple_elements(("ami", "ari", "aki",
                                                 "bare", "ovf"))
    _DISKS_CHOICES = double_tuple_elements(("ami", "ari", "aki", "vhd", "vdmk",
                                            "raw", "qcow2", "vdi", "iso"))

    container_format = forms.ChoiceField(choices=_CONTAINERS_CHOICES)
    disk_format = forms.ChoiceField(choices=_DISKS_CHOICES)
    min_ram = forms.IntegerField(min_value=0, initial=0, required=False)
    min_disk = forms.IntegerField(min_value=0, initial=0, required=False)


class CreateHeatAssetForm(CreateAssetForm):
    _TEMPLATES_CHOICES = double_tuple_elements(("2013-05-23", "2014-10-16",
                                                "2015-04-30", "2015-10-15"))

    environment = forms.CharField(max_length=255)
    template_version = forms.ChoiceField(choices=_TEMPLATES_CHOICES)


class CreateMuranoAssetForm(CreateAssetForm):
    _PACKAGES_TYPES = double_tuple_elements(("Application", "Library"))

    fqn = forms.CharField(label="Fully qualified name", max_length=255)
    package_type = forms.ChoiceField(choices=_PACKAGES_TYPES)


class CreateBundleAssetForm(CreateAssetForm):
    pass


class CreateToscaAssetForm(CreateAssetForm):
    _TEMPLATES_CHOICES = double_tuple_elements(("yaml", "csar"))

    def clean_mins_maxs(self, value):
        cleaned = self.cleaned_data[value]
        if cleaned:
            splitted = cleaned.split()
            if len(splitted) != 3 or not all(x.isdigit() for x in splitted):
                raise ValidationError("{0} input is incorrect".format(value))

        return cleaned

    def clean_mins(self):
        return self.clean_mins_maxs(value="mins")

    def clean_maxs(self):
        return self.clean_mins_maxs(value="maxs")

    template_format = forms.ChoiceField(choices=_TEMPLATES_CHOICES)
    # FIX Not sure what these fields mean.
    ever_mins = forms.CharField(label="Ever mins array",
                                help_text="three integers"
                                          " with space separator",
                                required=False)
    ever_maxs = forms.CharField(label="Ever maxs array",
                                help_text="three integers"
                                          " with space separator",
                                required=False)
