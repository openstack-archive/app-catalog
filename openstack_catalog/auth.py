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

import json
import pickle
import uuid

from flask import Flask
from flask import redirect
from flask import request
from flask import Response
from flask import session
from flask import sessions
import memcache
from openid.association import Association
from openid.consumer import consumer
from openid.extensions import sreg
from openid.store.interface import OpenIDStore
from openstack_catalog import settings
import requests


class MemcachedStore(OpenIDStore):

    def __init__(self, server='127.0.0.1:11211', prefix='_aoo_openid_oid',
                 time=30):
        self.time = 30
        self.prefix = prefix
        self.mc = memcache.Client([server], debug=1)

    def _get_key(self, server_url, handle):
        return self.prefix + server_url + handle

    def storeAssociation(self, server_url, association):
        key = self._get_key(server_url, association.handle)
        self.mc.set(key, association.serialize(), time=self.time)

    def getAssociation(self, server_url, handle=''):
        key = self._get_key(server_url, handle)
        data = self.mc.get(key)
        if data:
            return Association.deserialize(data)

    def useNonce(self, server_url, timestamp, salt):
        key = '%s-%s-%s' % (server_url, timestamp, salt)
        return self.mc.add(key, '1', time=self.time)


class Session(dict, sessions.SessionMixin):
    pass


class MCSessionInterface(sessions.SessionInterface):

    def __init__(self, mc):
        self.mc = mc

    def open_session(self, app, request):
        self.sid = request.cookies.get(settings.SESSION_COOKIE_NAME, None)
        if self.sid:
            data = self.mc.get(self.sid)
            if data:
                data = pickle.loads(data)
                return Session(**data)
        return Session()

    def save_session(self, app, session, response):
        if not self.sid:
            self.sid = uuid.uuid4().hex
        self.mc.set(self.sid, pickle.dumps(dict(session)),
                    time=settings.SESSION_EXPIRES)
        response.set_cookie(settings.SESSION_COOKIE_NAME, self.sid,
                            domain=settings.DOMAIN)


store = MemcachedStore(server=settings.MEMCACHED_SERVER)
auth = Flask('auth')
auth.debug = True
auth.session_interface = MCSessionInterface(store.mc)


@auth.route('/login')
def login():
    c = consumer.Consumer(session, store)
    request = c.begin(settings.LAUNCHPAD_LOGIN_URL)
    sreg_request = sreg.SRegRequest(required=['fullname', 'email', 'nickname'])
    request.addExtension(sreg_request)
    data = request.htmlMarkup(settings.BASE_URL,
                              return_to=settings.OPENID_RETURN_URL)
    return Response(data, status=200, mimetype='text/html')


@auth.route('/process')
def process():
    c = consumer.Consumer(session, store)
    info = c.complete(request.args, settings.OPENID_RETURN_URL)
    if info.status == consumer.CANCEL:
        return Response('Cancelled', status=200, mimetype='text/plain')
    if info.status != consumer.SUCCESS:
        return Response('Error', status=200, mimetype='text/plain')
    sreg_resp = sreg.SRegResponse.fromSuccessResponse(info)
    session['email'] = sreg_resp['email']
    session['fullname'] = sreg_resp['fullname']
    session['nickname'] = sreg_resp['nickname']
    session['launchpad_teams'] = get_launchpad_teams(session['nickname'])
    return redirect(settings.BASE_URL)


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(settings.BASE_URL)


@auth.route('/info')
def info():
    auth_info = get_auth_info(request)
    return Response(json.dumps(auth_info), status=200,
                    mimetype='application/json')


def get_launchpad_teams(nickname):
    url = settings.LAUNCHPAD_API_URL + "/~%s/super_teams" % nickname
    r = requests.get(url)
    return [e['name'] for e in r.json()["entries"]]


def get_auth_info(request):
    session = auth.session_interface.open_session(auth, request)
    response = {}
    for key in session:
        if key in {"nickname", "fullname", "email", "launchpad_teams"}:
            response[key] = session[key]
    return response
