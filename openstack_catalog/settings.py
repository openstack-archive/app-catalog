# -*- coding: utf-8 -*-

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

"""
Django settings for openstack_catalog project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os.path

from openstack_catalog.static_settings import get_staticfiles_dirs

DOMAIN = "localhost.localdomain:8000"
BASE_URL = "http://%s" % DOMAIN
OPENID_RETURN_URL = BASE_URL + "/auth/process"

SESSION_COOKIE_NAME = "s.aoo"
SESSION_EXPIRES = 86400
SESSION_SECURE = False
MEMCACHED_SERVER = "127.0.0.1:11211"

LAUNCHPAD_API_URL = "https://api.launchpad.net/devel"
LAUNCHPAD_LOGIN_URL = 'https://login.launchpad.net/'
LAUNCHPAD_ADMIN_GROUPS = {'app-catalog-core', }

GLARE_URL = 'http://127.0.0.1:9494'
PUBLIC_GLARE_URL = 'http://localhost:9494'
GLARE_TENANT = 'app-catalog'

ASSETS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                              'web/static/assets.yaml'))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'web',
                                           'static'))
STATICFILES_DIRS = get_staticfiles_dirs(STATIC_URL)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'notused'

DEBUG = True
ALLOWED_HOSTS = []

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_PATH + '/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True
        },
    },
]

COMPRESS_ENABLED = False
COMPRESS_CSS_HASHING_METHOD = 'hash'
COMPRESS_PARSER = 'compressor.parser.HtmlParser'

COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL,
}


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'compressor',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'openstack_catalog.urls'
WSGI_APPLICATION = 'openstack_catalog.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Override some values from local_settings.py if found
_LOCAL_SETTINGS_PATH = os.environ.get("LOCAL_SETTINGS_PATH",
                                      "/etc/openstack-catalog")
if os.path.isfile(os.path.join(_LOCAL_SETTINGS_PATH, 'local_settings.py')):
    import sys
    sys.path.insert(0, _LOCAL_SETTINGS_PATH)
    from local_settings import *  # noqa
    sys.path.pop(0)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
