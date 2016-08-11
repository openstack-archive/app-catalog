App-Catalog API v2.0
####################

Anonymous API
=============

These methods are available for anonymous users, and works in the same way as for any authorized user.

List public artifacts of specified type
---------------------------------------

GET /api/v2/public/<artifact_type>

List recently created/updated artifacts
---------------------------------------

GET /api/v2/recent

Show artifact details
---------------------

GET /api/v2/public/<artifact_type>/<artifact_id>

User API
========

This methods are available for all users authorized via Ubuntu One OpenID

Get user info
-------------

GET /api/v2/auth/info

Create a comment for artifact
-----------------------------

POST /api/v2/comment/<artifact_type>/<artifact_id>

Vote for artifact
-----------------

POST /api/v2/rating/<artifact_type>/<artifact_id>

Create a draft
--------------

POST /api/v2/db/artifacts/<artifact_type>

Edit own draft
--------------

PATCH /api/v2/db/artifacts/<artifact_type>/<artifact_id>

Activate a draft
----------------

PATCH /api/v2/db/artifacts/<artifact_type>/<artifact_id>

Admin API
=========

These methods are available for admins. Admin is a member of specified launcpad team.

List drafts
-----------

GET /api/v2/drafts/<artifact_type>

Approve draft
-------------

PATCH /api/v2/db/artifacts/<artifact_type>/<artifact_id>

Verify API
==========

These methods are available for verifiers. Some CI systems are able get notification when new artifact
is drafted, and then download and test it somehow.

Publish verification results
----------------------------

POST /api/v2/verify/<artifact_type>/<artifact_id>
