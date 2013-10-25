# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""clear SQLAlchemy migrate information for MediaCore (switching to alembic)

added: 2013-05-15 (v0.11dev)

Revision ID: 4c9f4cfc6085
Revises: 3b2f74a50399
Create Date: 2013-05-14 22:42:51.320534
"""

from alembic.op import execute, inline_literal

from sqlalchemy import Integer, Unicode, UnicodeText
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '4c9f4cfc6085'
down_revision = '3b2f74a50399'


migrate_table = table('migrate_version', 
    column('repository_id', Unicode(250)),
    column('repository_path', UnicodeText),
    column('version', Integer),
)


def upgrade():
    # let's stay on the safe side: theoretically the migrate table might have
    # been used by other plugins.
    execute(
        migrate_table.delete().\
            where(migrate_table.c.repository_id==inline_literal(u'MediaCore Migrations'))
    )

def downgrade():
    execute(
        migrate_table.insert().\
            values({
                'repository_id': inline_literal(u'MediaCore Migrations'),
                'version': inline_literal(57),
            })
    )

