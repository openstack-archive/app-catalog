from openstack_catalog import wsgi_django

from openstack_catalog.api import api

from werkzeug.wsgi import DispatcherMiddleware

application = DispatcherMiddleware(wsgi_django.application, {'/api': api})
