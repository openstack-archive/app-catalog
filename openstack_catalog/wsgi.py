from werkzeug.wsgi import DispatcherMiddleware
import wsgi_django

from flask import Flask

flasktest = Flask('foo')
flasktest.debug = True

@flasktest.route('/')
def hello_world():
    return 'Hello World!'

application = DispatcherMiddleware(wsgi_django.application, {'/flasktest': flasktest})
