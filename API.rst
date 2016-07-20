
Methods to implement
####################

List artifacts of specified type
================================

Such queries cannot be processed by Glare directly because fulltext search
and `list only latest version` features are not supported. Also additional
info like ratings culd not be stored in Glare database. All this issues
might be solved with Searchlight.

Show artifact details
=====================

Additional info like user comments, votes etc should be stored in own database.

This may be solved in two ways:

 * AppCatalog can get data from Glare and extend it with additional info stored
   in separate database.
 * Web client retrieve main data from Glare directly and get additional data
   from AppCatalog.

Add comments, stars
===================

This does not intersects with Glare at all.


Create drafts, edit and approve
===============================

These actions are fully supported by Glare.
