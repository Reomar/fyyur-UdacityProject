"""empty message

Revision ID: 8990ba537eaa
Revises: 77901eb0df56
Create Date: 2020-11-18 21:55:39.479171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8990ba537eaa'
down_revision = '77901eb0df56'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'genres')
    # ### end Alembic commands ###