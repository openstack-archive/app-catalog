===================================
GLARE plugin for app-catalog assets
===================================

This folder contains source code for GLARE plugin for app catalog assets.

This plugin defines schema for all the assets currently supported by the app
catalog.


Running GLARE localy
--------------------

To test this plugin locally you would need to clone latest glance source code:

.. code-block:: console

    git clone git://git.openstack.org/openstack/app-catalog
    git clone git://git.openstack.org/openstack/glance
..

*NOTE*: In Liberty release glare was called glance v3 api. It has been
moved into a separate service since then. Module paths changed during this
transition, therefore this plugin is not compatible with liberty code.

Minimal configuration is required, for glare to run correctly.
Edit ``etc/glance-glare.conf``, to specify where glare would actually
store it's binaries and database connection string.

For example:

.. code-block:: ini

    ...
    [glance_store]
    default_store = file
    filesystem_store_datadir = /tmp/glance/
    ...
    [database]
    connection = sqlite:///glare.sqlite
    ...
    [glare]
    custom_artifact_types_modules = openstack_app_catalog.artifacts
    enabled_artifact_types = glance_image,tosca_template,heat_template,murano_package
    ...
    [paste_deploy]
    flavor = session
    ...

..

And edit etc/glance-glare-paste.ini

.. code-block:: ini

    [pipeline:glare-api-session]
    pipeline = cors faultwrapper healthcheck versionnegotiation session context rootapp

    [filter:session]
    paste.filter_factory = openstack_app_catalog.middlewares:SessionMiddleware.factory
    memcached_server = 127.0.0.1:11211
    session_cookie_name = s.aoo

..

Run database migrations:

.. code-block:: console

    tox -evenv
    .tox/venv/bin/glance-manage --config-file etc/glance-glare.conf db upgrade
..

Import the plugin into glare's virtual environment:

.. code-block:: console

    .tox/venv/bin/pip install -e ../app-catalog/contrib/glare/
..

Run glare

.. code-block:: console

    .tox/venv/bin/glance-glare --config-file ./etc/glance-glare.conf
..

At this point glare service should be running and should contain all the
Artifact Types defined in this plugin.

To access list of all the artifact types loaded access
``http://127.0.0.1:9494/schemas``.
