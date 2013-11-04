# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import sql

class APIException(Exception):
    """
    API Usage Error -- wrapper for providing helpful error messages.
    TODO: Actually display these messages!!
    """

def get_order_by(order, columns):
    """ Discover the order by passed in """

    # Split the order into two parts, column and direction
    if not order:
        order_col, order_dir = 'publish_on', 'desc'
    else:
        try:
            order_col, order_dir = unicode(order).strip().lower().split(' ')
            assert order_dir in ('asc', 'desc')
        except:
            raise APIException, 'Invalid order format, must be "column asc/desc", given "%s"' % order

    # Get the order clause for the given column name
    try:
        order_attr = columns[order_col]
    except KeyError:
        raise APIException, 'Not allowed to order by "%s", please pick one of %s' % (order_col, ', '.join(columns.keys()))

    # Normalize to something that can be used in a query
    if isinstance(order_attr, basestring):
        order = sql.text(order_attr % (order_dir == 'asc' and 'asc' or 'desc'))
    else:
        # Assume this is an sqlalchemy InstrumentedAttribute
        order = getattr(order_attr, order_dir)()

    return order
