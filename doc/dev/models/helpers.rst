.. _dev_models_helpers:

=============
Model Helpers
=============

Fetching Records
================

.. autofunction:: mediacore.model.fetch_row

Slugs
=====

.. autofunction:: mediacore.model.slugify

.. autofunction:: mediacore.model.get_available_slug


Statuses
========

.. automodule:: mediacore.model.status

Representation
--------------

.. autoclass:: Status
   :members:

.. autoclass:: StatusBit
   :members:

Database Columns
----------------

.. autoclass:: StatusType
   :members:

Mapping Extensions & Helpers
----------------------------

.. autoclass:: StatusTypeExtension
   :members:

.. autoclass:: StatusComparator
   :members:

Helpers
-------

.. autofunction:: status_where

.. autofunction:: status_column_property

.. autofunction:: map_values_to_bits

