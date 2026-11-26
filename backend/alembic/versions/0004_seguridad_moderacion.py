"""Add shared login rate limit buckets."""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_rate_limits",
        sa.Column("ip_hash", sa.String(64), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("ip_hash", "window_start", name="pk_login_rate_limits"),
    )
    op.create_index("ix_login_rate_limits_window_start", "login_rate_limits", ["window_start"])


def downgrade() -> None:
    op.drop_index("ix_login_rate_limits_window_start", table_name="login_rate_limits")
    op.drop_table("login_rate_limits")
