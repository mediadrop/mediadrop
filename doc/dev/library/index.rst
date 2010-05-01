.. _dev_lib_toplevel:

=======
Library
=======

Base
----

.. autoclass:: mediacore.lib.base.BaseController
   :members:
   :show-inheritance:

Helpers
-------

.. automodule:: mediacore.lib.helpers


Controllers
-----------

.. autofunction:: url_for

.. autofunction:: redirect

.. autofunction:: mediacore.lib.paginate.paginate


XHTML Handling
--------------

.. autofunction:: clean_xhtml

.. autofunction:: truncate_xhtml

.. autofunction:: strip_xhtml

.. autofunction:: line_break_xhtml

.. autofunction:: list_acceptable_xhtml


Thumbnail Images
----------------

.. autofunction:: thumb_path

.. autofunction:: thumb_paths

.. autofunction:: thumb_url

.. autofunction:: thumb

.. autofunction:: resize_thumb

.. autofunction:: create_default_thumbs_for

.. autoclass:: ThumbDict


Misc
----

.. autofunction:: duration_from_seconds

.. autofunction:: duration_to_seconds

.. autofunction:: truncate

.. autofunction:: list_accepted_extensions

.. autofunction:: best_json_content_type

.. autofunction:: append_class_attr

.. autofunction:: embeddable_player

.. autofunction:: get_featured_category

.. autofunction:: filter_library_controls

.. autofunction:: is_admin

.. autofunction:: fetch_setting

.. autofunction:: gravatar_from_email

.. autofunction:: pretty_file_size

.. autofunction:: delete_files

.. autofunction:: add_transient_message


Decorators
----------

.. automodule:: mediacore.lib.decorators

.. autofunction:: expose

.. autofunction:: expose_xhr

.. autofunction:: paginate

.. autofunction:: validate

