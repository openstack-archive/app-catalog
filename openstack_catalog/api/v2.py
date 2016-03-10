# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from flask import Response
from flask import stream_with_context
import requests

from openstack_catalog.api import api
from openstack_catalog import settings


@api.route('/v2/<path:url>')
def v2_index(url):
    glare_url = "{}/v0.1/{}".format(settings.GLARE_URI, url)
    req = requests.get(glare_url, stream=True)
    resp = Response(
        stream_with_context(req.iter_content()),
        content_type=req.headers['content-type'])
    return resp
