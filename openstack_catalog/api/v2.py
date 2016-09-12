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

import json
import random
import requests

from flask import Response
import memcache
from openstack_catalog.api import api
from openstack_catalog import settings


RECENT_CACHE_KEY = '_recent_'
RECENT_CACHE_TIME = 1200

cache = memcache.Client([settings.MEMCACHED_SERVER])


@api.route('/v2/recent')
def recent():
    response = cache.get(RECENT_CACHE_KEY)
    if not response:
        assets = []
        for artifact_type in ('images', 'heat_templates',
                              'murano_packages'):
            url = '%s/artifacts/%s' % (settings.GLARE_URL,
                                       artifact_type)
            url = '%s?sort=updated_at&version=latest' % url
            for asset in requests.get(url).json()[artifact_type][:5]:
                if artifact_type == 'murano_packages':
                    name = asset['display_name']
                else:
                    name = asset['name']
                assets.append({
                    'name': name,
                    'type': artifact_type,
                    'id': asset['id'],
                    'icon': asset['icon'] is not None,
                })
        random.shuffle(assets)
        response = json.dumps(assets[:5])
        cache.set(RECENT_CACHE_KEY, response, time=RECENT_CACHE_TIME)
    return Response(response, mimetype='application/json')
