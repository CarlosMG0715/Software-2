"""Re-key author pseudonyms with the private server secret.

Keep HASH_SALT unchanged until this migration has completed. SECRET_KEY must
remain stable afterward or users will lose ownership of their existing activity.
"""
import hashlib
import hmac

from alembic import op
from sqlalchemy import text

from app.config import settings

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    user_ids = connection.execute(text("SELECT id FROM usuarios")).scalars().all()
    for user_id in user_ids:
        old_hash = hmac.new(
            settings.hash_salt.encode(), f"usuario:{user_id}".encode(), hashlib.sha256
        ).hexdigest()
        new_hash = hmac.new(
            settings.secret_key.encode(), f"resena:autor:usuario:{user_id}".encode(), hashlib.sha256
        ).hexdigest()
        connection.execute(
            text("UPDATE resenas SET autor_hash = :new WHERE autor_hash = :old"),
            {"new": new_hash, "old": old_hash},
        )
        connection.execute(
            text("UPDATE reportes SET reportante_hash = :new WHERE reportante_hash = :old"),
            {"new": new_hash, "old": old_hash},
        )
        connection.execute(
            text("UPDATE votos_utilidad SET usuario_hash = :new WHERE usuario_hash = :old"),
            {"new": new_hash, "old": old_hash},
        )


def downgrade() -> None:
    connection = op.get_bind()
    user_ids = connection.execute(text("SELECT id FROM usuarios")).scalars().all()
    for user_id in user_ids:
        new_hash = hmac.new(
            settings.secret_key.encode(), f"resena:autor:usuario:{user_id}".encode(), hashlib.sha256
        ).hexdigest()
        old_hash = hmac.new(
            settings.hash_salt.encode(), f"usuario:{user_id}".encode(), hashlib.sha256
        ).hexdigest()
        connection.execute(
            text("UPDATE resenas SET autor_hash = :old WHERE autor_hash = :new"),
            {"new": new_hash, "old": old_hash},
        )
        connection.execute(
            text("UPDATE reportes SET reportante_hash = :old WHERE reportante_hash = :new"),
            {"new": new_hash, "old": old_hash},
        )
        connection.execute(
            text("UPDATE votos_utilidad SET usuario_hash = :old WHERE usuario_hash = :new"),
            {"new": new_hash, "old": old_hash},
        )
