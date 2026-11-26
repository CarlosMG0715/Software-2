"""Route existing public reviews through moderation once."""
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE resenas SET estado = 'pendiente' WHERE estado = 'visible'")


def downgrade() -> None:
    op.execute("UPDATE resenas SET estado = 'visible' WHERE estado = 'pendiente'")
