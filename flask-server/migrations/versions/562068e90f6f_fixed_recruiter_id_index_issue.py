"""Fixed recruiter_id index issue

Revision ID: 562068e90f6f
Revises: 
Create Date: 2024-12-09 17:38:16.520169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '562068e90f6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.create_index('ix_recruiter_id', ['recruiter_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_recruiter_id')

    # ### end Alembic commands ###
