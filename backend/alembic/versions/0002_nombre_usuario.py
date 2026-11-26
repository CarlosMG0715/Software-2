"""Añade el nombre visible a los usuarios."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("nombre", sa.String(150), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("usuarios", "nombre")
