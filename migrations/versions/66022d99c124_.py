"""empty message

Revision ID: 66022d99c124
Revises: d5c481cf29bb
Create Date: 2020-08-25 21:31:23.016593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66022d99c124'
down_revision = 'd5c481cf29bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.drop_column('Artist', 'web')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('web', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
