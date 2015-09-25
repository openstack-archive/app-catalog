from werkzeug.wsgi import DispatcherMiddleware
import wsgi_django

from api import api

application = DispatcherMiddleware(wsgi_django.application, {'/api': api})
