"""empty message

Revision ID: 377dff46ea2c
Revises: ff157d3ebaf8
Create Date: 2020-08-25 17:41:33.664873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '377dff46ea2c'
down_revision = 'ff157d3ebaf8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_genres',
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.PrimaryKeyConstraint('genre_id', 'artist_id')
    )
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_table('artist_genres')
    op.drop_table('Genre')
    # ### end Alembic commands ###