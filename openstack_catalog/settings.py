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

import os
import os.path

from static_settings import get_staticfiles_dirs

STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'web',
                                           'static'))
STATICFILES_DIRS = get_staticfiles_dirs(STATIC_URL)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'notused'

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    PROJECT_PATH + '/templates/',
)

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
