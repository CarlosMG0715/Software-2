"""esquema inicial

Revision ID: 0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profesores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("departamento", sa.String(150), nullable=False),
        sa.Column("facultad", sa.String(150), nullable=False),
    )
    op.create_table(
        "asignaturas",
        sa.Column("codigo", sa.String(20), primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("facultad", sa.String(150), nullable=False),
        sa.Column("creditos", sa.Integer, nullable=False),
    )
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("correo", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("verificado", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("rol", sa.String(20), nullable=False, server_default="ESTUDIANTE"),
        sa.Column("intentos_fallidos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("bloqueado_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("profesor_id", sa.Integer, sa.ForeignKey("profesores.id"), nullable=True),
    )
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"], unique=True)
    op.create_table(
        "ofertas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("profesor_id", sa.Integer, sa.ForeignKey("profesores.id"), nullable=False),
        sa.Column("asignatura_codigo", sa.String(20), sa.ForeignKey("asignaturas.codigo"), nullable=False),
        sa.Column("periodo", sa.String(10), nullable=False),
        sa.Column("seccion", sa.String(10), nullable=False),
        sa.UniqueConstraint("profesor_id", "asignatura_codigo", "periodo", "seccion", name="uq_oferta"),
    )
    op.create_table(
        "resenas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("oferta_id", sa.Integer, sa.ForeignKey("ofertas.id"), nullable=False),
        sa.Column("autor_hash", sa.String(64), nullable=False),
        sa.Column("claridad", sa.SmallInteger, nullable=False),
        sa.Column("exigencia", sa.SmallInteger, nullable=False),
        sa.Column("puntualidad", sa.SmallInteger, nullable=False),
        sa.Column("recomienda", sa.Boolean, nullable=False),
        sa.Column("comentario", sa.Text, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String(40)), nullable=False, server_default="{}"),
        sa.Column("estado", sa.String(20), nullable=False, server_default="visible"),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("autor_hash", "oferta_id", name="uq_resena_autor_oferta"),
    )
    op.create_index("ix_resenas_oferta_id", "resenas", ["oferta_id"])
    op.create_index("ix_resenas_autor_hash", "resenas", ["autor_hash"])
    op.create_table(
        "reportes",
        sa.Column("resena_id", sa.Integer, sa.ForeignKey("resenas.id", ondelete="CASCADE"), primary_key=True, autoincrement=False),
        sa.Column("reportante_hash", sa.String(64), primary_key=True),
        sa.Column("motivo", sa.String(300), nullable=False),
    )
    op.create_table(
        "votos_utilidad",
        sa.Column("resena_id", sa.Integer, sa.ForeignKey("resenas.id", ondelete="CASCADE"), primary_key=True, autoincrement=False),
        sa.Column("usuario_hash", sa.String(64), primary_key=True),
        sa.Column("es_util", sa.Boolean, nullable=False),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("accion", sa.String(200), nullable=False),
        sa.Column("ejecutado_por", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    for t in ("audit_log", "votos_utilidad", "reportes", "resenas", "ofertas", "usuarios", "asignaturas", "profesores"):
        op.drop_table(t)