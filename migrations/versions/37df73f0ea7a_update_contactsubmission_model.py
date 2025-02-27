"""Update ContactSubmission model

Revision ID: 37df73f0ea7a
Revises: 
Create Date: 2024-06-20 14:52:39.554270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37df73f0ea7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contact_submission', schema=None) as batch_op:
        batch_op.alter_column('submitted_at',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contact_submission', schema=None) as batch_op:
        batch_op.alter_column('submitted_at',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###
