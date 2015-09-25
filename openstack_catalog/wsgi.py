from werkzeug.wsgi import DispatcherMiddleware
from openstack_catalog import wsgi_django

from openstack_catalog.api import api

application = DispatcherMiddleware(wsgi_django.application, {'/api': api})
