from openstack_catalog import wsgi_django

from openstack_catalog.api import api
from openstack_catalog.auth import auth

from werkzeug.wsgi import DispatcherMiddleware

application = DispatcherMiddleware(wsgi_django.application, {'/api': api,
                                                             '/auth': auth})
