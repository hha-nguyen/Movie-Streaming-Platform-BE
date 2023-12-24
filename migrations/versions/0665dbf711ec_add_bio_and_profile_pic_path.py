"""Add bio and profile_pic_path

Revision ID: 0665dbf711ec
Revises: 0ca1a411b383
Create Date: 2019-10-19 17:12:11.884536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0665dbf711ec'
down_revision = '0ca1a411b383'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('bio', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('profile_pic_path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_pic_path')
    op.drop_column('users', 'bio')
    # ### end Alembic commands ###