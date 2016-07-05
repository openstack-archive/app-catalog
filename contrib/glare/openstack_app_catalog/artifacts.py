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

from glance.db.glare import artifact_api
from glance.objects import base
from glance.objects import fields as glare_fields
from glance.objects.fields import attribute
from oslo_versionedobjects import fields


def dict_validator(allowed_keys=None, required_keys=None, field_name=None):
    def validator(field):
        if allowed_keys:
            unexpected_keys = set(field.keys()) - allowed_keys
            if unexpected_keys:
                fmt = "Unexpected keys: %s (allowed keys %s) for field %s"
                raise ValueError(fmt % (unexpected_keys, allowed_keys, field_name))
        if required_keys:
            missing_keys = required_keys - set(field.keys())
            if missing_keys:
                raise ValueError("Missing keys: %s" % missing_keys)
    return validator

_icon_keys = {"url", "top", "left", "height"}
icon_validator = dict_validator(allowed_keys=_icon_keys,
                                required_keys=_icon_keys,
                                field_name="icon")
_provided_by_keys = {"name", "href", "company"}
provided_by_validator = dict_validator(allowed_keys=_provided_by_keys,
                                       required_keys=_provided_by_keys,
                                       field_name="provided_by")
supported_by_validator = dict_validator(allowed_keys={"name", },
                                        required_keys={"name", },
                                        field_name="supported_by")


class BaseAsset(base.BaseArtifact):
    VERSION = '0.1'

    fields = {
        'depends': attribute(glare_fields.Dependency,
                             validators=[],
                             required_on_activate=False,
                             sortable=False,
                             filter_ops=[]),
        'provided_by': attribute(glare_fields.Dict,
                                 filter_ops=[],
                                 validators=[provided_by_validator],
                                 required_on_activate=True,
                                 element_type=fields.String),
        'supported_by': attribute(glare_fields.Dict,
                                  validators=[supported_by_validator],
                                  filter_ops=[],
                                  required_on_activate=False,
                                  element_type=fields.String),
        'release': attribute(glare_fields.List,
                             filter_ops=[],
                             default=[],
                             validators=[],
                             required_on_activate=False,
                             element_type=fields.String),
        'icon': attribute(glare_fields.Dict,
                          validators=[icon_validator],
                          required_on_activate=False,
                          filter_ops=[],
                          element_type=fields.String),
        'license': attribute(fields.StringField,
                             validators=[],
                             required_on_activate=True,
                             filter_ops=[]),
        'license_url': attribute(fields.StringField,
                                 validators=[],
                                 required_on_activate=False,
                                 filter_ops=[]),
        'attributes': attribute(glare_fields.Dict,
                                validators=[],
                                required_on_activate=False,
                                filter_ops=[],
                                element_type=fields.String),
    }

    @classmethod
    def get_type_name(cls):
        return "base_artifact"

    @classmethod
    def init_db_api(cls):
        return artifact_api.ArtifactAPI(cls)


class GlanceImageAsset(BaseAsset):

    fields = {
        'container_format': attribute(fields.StringField,
                                      filter_ops=[],
                                      required_on_activate=True),
        'disk_format': attribute(fields.StringField,
                                 filter_ops=[],
                                 required_on_activate=True),
        'min_ram': attribute(fields.IntegerField,
                             filter_ops=[],
                             required_on_activate=False),
        'min_disk': attribute(fields.IntegerField,
                              filter_ops=[],
                              required_on_activate=False),
        'image': attribute(glare_fields.BlobField,
                           required_on_activate=False,
                           mutable=False,
                           sortable=False,
                           filter_ops=[]),
        'image_indirect_url': attribute(fields.StringField,
                                        filter_ops=[],
                                        required_on_activate=False),
        }

    @classmethod
    def get_type_name(cls):
        return "glance_image"


class TOSCATemplateAsset(BaseAsset):

    fields = {
        'template_format': attribute(fields.StringField,
                                     required_on_activate=True),
        'template': attribute(glare_fields.BlobField,
                              required_on_activate=True)
    }

    @classmethod
    def get_type_name(cls):
        return "tosca_template"
