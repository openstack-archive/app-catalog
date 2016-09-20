===================================
GLARE plugin for app-catalog assets
===================================

Install dependencies:

.. code-block:: console

    sudo apt-get install memcached python-dev libpq-dev libffi-dev python-pip python-dev libpq-dev
    sudo pip install --upgrade pip tox
    # create and activate venv
    virtualenv appcatalog --p python2.7
    cd appcatalog
    . bin/activate
..

Running GLARE localy
--------------------

To test this plugin locally you need to install glare either via pip or git:

NOTE: run this commands with venv activated (`. appcatalog/bin/activate`)

.. code-block:: console

    git clone git://git.openstack.org/openstack/glare
    pip install -e glare
    # OR
    pip install glare_dev
..

Install app-catalog in the same way:

.. code-block:: console

    git clone git://git.openstack.org/openstack/app-catalog
    pip install -e app-catalog
    # OR
    pip install openstack_app_catalog
..

Create ``etc/glare.conf``, to specify where glare would actually
store it's binaries and database connection string.

For example:

.. code-block:: ini

    [DEFAULT]
    default_api_limit = 100
    allow_anonymous_access = true
    [glance_store]
    default_store = file
    filesystem_store_datadir = /tmp/blobs
    [database]
    connection = sqlite:////tmp/glare.sqlite
    [paste_deploy]
    flavor = session
    [oslo_policy]
    policy_file = policy.json
..

Edit etc/glare-paste.ini

.. code-block:: ini

    [pipeline:glare-api-session]
    pipeline = cors faultwrapper healthcheck versionnegotiation session context glarev1api

    [filter:session]
    paste.filter_factory = openstack_catalog.plugins.glare.middlewares:SessionMiddleware.factory
    memcached_server = 127.0.0.1:11211
    session_cookie_name = s.aoo
..

Create etc/policy.json:

.. code-block:: json

    {
        "context_is_admin": "role:app-catalog-core"
    }
..

Run database migrations:

.. code-block:: console

    glare-db-manage --config-file etc/glare.conf upgrade
..

Run glare

.. code-block:: console

    glare-api --config-file etc/glare.conf
..

At this point glare service should be running.

Open another console, activate virtualenv and upload artifacts to Glare

.. code-block:: console

    cd appcatalog
    . bin/activate
    app-catalog-import-assets
..

Create local_setting.py file (if necessary)

.. code-block:: python

    DOMAIN = "example.com"
    BASE_URL = "http://%s:8000" % DOMAIN
    OPENID_RETURN_URL = BASE_URL + "/auth/process"
..

Run app catalog

.. code-block:: console

    app-catalog-manage runserver 0.0.0.0:8000
..

Make sure you have localhost.localdomain in /etc/hosts::

    127.0.0.1       localhost localhost.localdomain
..

At this point app catalog should be available by this url: http://localhost.localdomain:8000/
