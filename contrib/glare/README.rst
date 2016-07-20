===================================
GLARE plugin for app-catalog assets
===================================

This folder contains source code for GLARE plugin for app catalog assets.

This plugin defines schema for all the assets currently supported by the app
catalog.

Install app catalog:

.. code-block:: console
    git clone git://git.openstack.org/openstack/app-catalog
    cd app-catalog
    git fetch https://git.openstack.org/openstack/app-catalog refs/changes/33/337633/17 && git checkout FETCH_HEAD
    cd ..
..

Running GLARE localy
--------------------

To test this plugin locally you would need to clone latest glare source code:

.. code-block:: console
    git clone git://git.openstack.org/openstack/glare
    cd glare
    tox -evenv -- oslo-config-generator --config-file etc/oslo-config-generator/glare.conf --output-file etc/glare.conf
..

Edit ``etc/glare.conf``, to specify where glare would actually
store it's binaries and database connection string.

For example:

.. code-block:: ini
    ...
    [DEFAULT]
    allow_anonymous_access = true
    [glance_store]
    default_store = file
    filesystem_store_datadir = /tmp/blobs
    ...
    [database]
    connection = sqlite:////tmp/glare.sqlite
    ...
    [glare]
    custom_artifact_types_modules = openstack_app_catalog.artifacts
    enabled_artifact_types = glance_image,tosca_template,heat_template,murano_package
    ...
    [paste_deploy]
    flavor = session
    ...
    [oslo_policy]
    policy_file = glare-policy.json
..

And edit etc/glare-paste.ini

.. code-block:: ini
    [pipeline:glare-api-session]
    pipeline = cors faultwrapper healthcheck versionnegotiation session context glarev1api

    [filter:session]
    paste.filter_factory = openstack_app_catalog.middlewares:SessionMiddleware.factory
    memcached_server = 127.0.0.1:11211
    session_cookie_name = s.aoo
..

Create etc/glare-policy.json:

.. code-block:: json
    {
        "context_is_admin": "role:app-catalog-core"
    }
..

Run database migrations:

.. code-block:: console
    tox -evenv -- glare-db-manage --config-file etc/glare.conf upgrade
..

Import the plugin into glare's virtual environment:

.. code-block:: console
    tox -evenv -- pip install -e ../app-catalog/contrib/glare/
..

Run glare

.. code-block:: console
    .tox/venv/bin/glare-api --config-file ./etc/glare.conf
..

At this point glare service should be running and should contain all the
Artifact Types defined in this plugin.


Run app catalog
---------------

Install memcached

.. code-block:: console
    apt-get install memcached
..

Run app catalog

.. code-block:: console
    # cd to app catalog directory
    .tox/venv/bin/python manage.py runserver 0.0.0.0:8000
..

Import artifacts from yaml file

.. code-block:: console
    # cd to app catalog directory
    .tox/venv/bin/python contrib/move_to_glare_10.py
..

At this point app catalog should be available by this url: http://localhost:8000/
