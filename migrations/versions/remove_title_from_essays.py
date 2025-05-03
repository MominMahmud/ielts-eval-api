"""remove title from essays

Revision ID: remove_title_from_essays
Revises: 6cbbd87b9d3f
Create Date: 2024-03-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_title_from_essays'
down_revision = '6cbbd87b9d3f'
branch_labels = None
depends_on = None

def upgrade():
    # Remove the title column from essays table
    op.drop_column('essays', 'title')

def downgrade():
    # Add back the title column
    op.add_column('essays', sa.Column('title', sa.String(), nullable=False)) 