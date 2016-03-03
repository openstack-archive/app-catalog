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

import sys

from django.forms.utils import ErrorDict
from django.shortcuts import render

from asset import Asset
import forms as aforms


def index(request):
    return render(request, 'index.html', {})


def new_asset(request):
    def asset_factory(*request_dict):
        type_name = request_dict[0]['type_name']
        if type_name == 'glance':
            caForm = aforms.CreateGlanceAssetForm(*request_dict)
        elif type_name == 'heat':
            caForm = aforms.CreateHeatAssetForm(*request_dict)
        elif type_name == 'murano':
            caForm = aforms.CreateMuranoAssetForm(*request_dict)
        elif type_name == 'bundle':
            caForm = aforms.CreateBundleAssetForm(*request_dict)
        elif type_name == 'tosca':
            caForm = aforms.CreateToscaAssetForm(*request_dict)
        else:
            caForm = aforms.CreateAssetForm(*request_dict)

        return caForm

    if request.is_ajax():
        template = 'create_asset_form.html'
    else:
        template = 'create_asset.html'

    if request.method == 'POST':
        caForm = asset_factory(request.POST, request.FILES)
        if caForm.is_valid():
            cleaned = caForm.cleaned_data
            asset = Asset(cleaned)
            draft = asset.prepare_data()
            sys.stdout.write('draft info:\n{0}\n'.format(draft))
            sys.stdout.write('file info:\n{0}\n'.format(
                             asset.bare_data['binary']))
    else:
        if request.is_ajax():
            caForm = asset_factory(request.GET)
            caForm._errors = ErrorDict()
        else:
            caForm = aforms.CreateGlanceAssetForm()

    return render(request, template, {'caForm': caForm})
