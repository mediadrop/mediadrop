.. _glossary:

========
Glossary
========

.. glossary::

    media
        A collection of 0 or more closely-related **audio** and/or **video**
        files and metadata that describes them.
        See :class:`mediadrop.model.media.Media` for the definition in code.

    slug
        A unique, search-engine-friendly identifier for an item. It is made up
        of purely alphanumeric characters and hyphens.

    status
        A set of pre-determined flags describing a content item:

            * publish
            * draft
            * trash
            * unencoded
            * unreviewed
            * user_flagged

        See :mod:`mediadrop.model.statuses`.

    tag
        A keyword or term that describes some aspect of a content item.
        Typically these can be more specific than :term:`topic`'s
        because they can be created on an *ad hoc* basis.

    topic
        A category of content. Unlike :term:`tag`'s these are not created
        on an *ad-hoc* basis: generally you confine yourself to a small
        list of topics because the list should be easy to read over for
        users.

    unencoded
        Audio or video that is not in a web-friendly format.

    unreviewed
        Audio or video that has been added, but doesn't have admin approval yet.

