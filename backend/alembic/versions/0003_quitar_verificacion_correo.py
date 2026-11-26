"""Quita el estado de verificación por correo de las cuentas."""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("usuarios", "verificado")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column("usuarios", sa.Column("verificado", sa.Boolean(), nullable=False, server_default=sa.false()))
