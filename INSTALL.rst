===================================
GLARE plugin for app-catalog assets
===================================

Install dependencies:

.. code-block:: console
    sudo apt-get install memcached python-dev libpq-dev libffi-dev python-pip python-dev libpq-dev
    sudo pip install --upgrade pip tox
..

Running GLARE localy
--------------------

To test this plugin locally you would need to clone latest glare source code:

.. code-block:: console
    git clone git://git.openstack.org/openstack/glare
    cd glare
..

Create ``etc/glare.conf``, to specify where glare would actually
store it's binaries and database connection string.

For example:

.. code-block:: ini
    ...
    [DEFAULT]
    allow_anonymous_access = true
    [glance_store]
    default_store = file
    filesystem_store_datadir = /tmp/blobs
    [database]
    connection = sqlite:////tmp/glare.sqlite
    [glare]
    custom_artifact_types_modules = openstack_catalog.plugins.glare.artifacts
    enabled_artifact_types = glance_image,tosca_template,heat_template,murano_package
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

Run glare

.. code-block:: console
    .tox/venv/bin/glare-api --config-file ./etc/glare.conf
..

At this point glare service should be running and should contain all the
Artifact Types defined in this plugin.


Install and run app catalog
---------------

.. code-block:: console
    pip install openstack_app_catalog
..

Upload artifacts to Glare

.. code-block:: console
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

At this point app catalog should be available by this url: http://localhost:8000/
