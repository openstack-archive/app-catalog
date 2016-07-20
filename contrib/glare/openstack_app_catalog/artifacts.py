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

import shutil
import tempfile

from glare.objects import attribute
from glare.objects import base
from glare.objects import fields as glare_fields
from glare.objects import validators
from toscaparser.tosca_template import ToscaTemplate

from oslo_versionedobjects import fields


Field = attribute.Attribute.init
DictField = attribute.DictAttribute.init
ListField = attribute.ListAttribute.init


class BaseAsset(base.BaseArtifact):
    VERSION = '0.1'

    fields = {
        'depends': ListField(glare_fields.Dependency,
                             required_on_activate=False),
        'provided_by': DictField(fields.String,
                                 validators=[
                                     validators.RequiredDictKeys(
                                         ['name', 'href', 'company']),
                                     validators.AllowedDictKeys(
                                         ['name', 'href', 'company'])],
                                 required_on_activate=True),
        'supported_by': DictField(fields.String,
                                  nullable=True,
                                  validators=[
                                      validators.RequiredDictKeys(['name']),
                                      validators.AllowedDictKeys(['name'])],
                                  required_on_activate=False),
        'release': ListField(fields.String,
                             default=[],
                             required_on_activate=False),
        'icon': Field(glare_fields.BlobField,
                      required_on_activate=False,
                      mutable=True,
                      sortable=False),
        'license': Field(fields.StringField,
                         required_on_activate=True),
        'license_url': Field(fields.StringField,
                             required_on_activate=False),
        'metadata': DictField(fields.String,
                              required_on_activate=False),
    }

    @classmethod
    def get_type_name(cls):
        return "base_artifact"


class GlanceImageAsset(BaseAsset):

    fields = {
        'container_format': Field(fields.StringField,
                                  required_on_activate=True),
        'disk_format': Field(fields.StringField,
                             required_on_activate=True),
        'min_ram': Field(fields.IntegerField,
                         required_on_activate=False),
        'min_disk': Field(fields.IntegerField,
                          required_on_activate=False),
        'image': Field(glare_fields.BlobField,
                       required_on_activate=False,
                       mutable=False,
                       sortable=False),
        'image_indirect_url': Field(fields.StringField,
                                    required_on_activate=False),
        'cloud_user': Field(fields.StringField,
                            required_on_activate=False),
        }

    @classmethod
    def get_type_name(cls):
        return "glance_image"


class TOSCATemplateAsset(BaseAsset):

    fields = {
        'template_format': Field(fields.StringField,
                                 required_on_activate=True),
        'template': Field(glare_fields.BlobField,
                          required_on_activate=True)
    }

    @classmethod
    def get_type_name(cls):
        return "tosca_template"

    @classmethod
    def validate_upload(cls, context, af, field_name, fd):
        suffix = "." + af.template_format
        tfd = tempfile.NamedTemporaryFile(prefix="aoo_tosca", suffix=suffix)
        shutil.copyfileobj(fd, tfd)
        ToscaTemplate(tfd.name)
        tfd.flush()
        tfd.seek(0)
        return tfd


class HeatTemplateAsset(BaseAsset):

    fields = {
        'environment': DictField(fields.String,
                                 required_on_activate=False,
                                 default={}),
        'template': Field(glare_fields.BlobField,
                          required_on_activate=True),
        'files': DictField(glare_fields.BlobFieldType,
                           required_on_activate=False,
                           default={})
    }

    @classmethod
    def get_type_name(cls):
        return "heat_template"


class MuranoPackageAsset(BaseAsset):

    fields = {
        'package': Field(glare_fields.BlobField,
                         required_on_activate=False),
        'package_name': Field(fields.StringField,
                              required_on_activate=True),
    }

    @classmethod
    def get_type_name(cls):
        return "murano_package"
