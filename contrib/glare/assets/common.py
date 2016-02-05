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

from glance.common.artifacts import definitions

href_mailto_pattern = ("^((https?://)[a-z][a-z0-9_-]+(\\.[a-z][a-z0-9_-]+)+"
                       "(/[a-z0-9\\._/~%\\-\\+&\\#\\?!=\\(\\)@]*)?)|"
                       "(mailto:[a-z][a-z0-9._-]+@[a-z][a-z0-9_-]+"
                       "(\\.[a-z][a-z0-9_-]+)+)$")

href_pattern = ("^((https?://)[a-z][a-z0-9_-]*(\\.[a-z][a-z0-9_-]*)+"
                "(/[a-z0-9\\._/~%\\-\\+&\\#\\?!=\\(\\)@]*)?)")


class AssetArtifact(definitions.ArtifactType):
    provided_by = definitions.Dict(
        required=True,
        mutable=False,
        properties={
            'name': definitions.String(required=True),
            'href': definitions.String(pattern=href_mailto_pattern,
                                       required=True,
                                       ),
            'company': definitions.String(),
            'irchandle': definitions.String(),
            },
        )

    supported_by = definitions.Dict(
        properties={
            'name': definitions.String(required=True),
            'href': definitions.String(pattern=href_mailto_pattern,
                                       required=True,
                                       ),
            'company': definitions.String(),
            'irchandle': definitions.String(),
            },
        )

    depends = definitions.ArtifactReferenceList()
    release = definitions.Array(
        min_size=1,
        item_type=definitions.String(
            allowed_values=[
                'Austin', 'Bexar', 'Cactus', 'Diablo',
                'Essex', 'Folsom', 'Grizzly',
                'Havana', 'Icehouse', 'Juno', 'Kilo',
                'Liberty', 'Mitaka', 'Newton', 'Ocata'])
    )
    icon = definitions.Dict(
        mutable=False,
        properties={
            "top": definitions.Integer(required=True),
            "left": definitions.Integer(required=True),
            "height": definitions.Integer(required=True),
            "url": definitions.String(
                required=True,
                pattern=href_pattern,
            ),
        },
    )

    license = definitions.String(
        pattern=("^(GPL .*)|(Apache .*)|(BSD .*)|(MIT)|"
                 "(Free <= [0-9]+ (Users|Nodes))|"
                 "(Multi-licensed OpenSource)|(Other)|(Unknown)$"),
        required=True, mutable=False)
    license_url = definitions.String(pattern=href_pattern, mutable=False)

    stored = definitions.Boolean(default=False)
    stored_object = definitions.BinaryObject()

    remote_object_url = definitions.String(
        pattern=href_pattern,
        mutable=False,
    )

    attributes = definitions.Dict(mutable=False)
    active = definitions.Boolean(default=True)
