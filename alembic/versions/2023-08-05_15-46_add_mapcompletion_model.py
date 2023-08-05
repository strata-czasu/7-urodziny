"""Add MapCompletion model

Revision ID: aeb6c0814481
Revises: b838b77e92a0
Create Date: 2023-08-05 15:46:00.378524+00:00

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "aeb6c0814481"
down_revision = "b838b77e92a0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "map_completion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["profile"], ["profile.id"], name="fk_map_completion_profile_id_profile"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("map_completion")
    # ### end Alembic commands ###