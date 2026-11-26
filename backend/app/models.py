import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Rol(str, enum.Enum):
    ESTUDIANTE = "ESTUDIANTE"
    DOCENTE = "DOCENTE"
    MODERADOR = "MODERADOR"
    ADMIN = "ADMIN"


class EstadoResena(str, enum.Enum):
    VISIBLE = "visible"
    OCULTA = "oculta"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    ELIMINADA = "eliminada"


ESTADOS_PUBLICOS = (EstadoResena.VISIBLE.value, EstadoResena.APROBADA.value)
TAGS_PREDEFINIDOS = ["Exámenes largos", "Toma asistencia", "Talleres en grupo", "Sube la nota fácil", "Buen material"]


class Profesor(Base):
    __tablename__ = "profesores"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    departamento: Mapped[str] = mapped_column(String(150))
    facultad: Mapped[str] = mapped_column(String(150))


class Asignatura(Base):
    __tablename__ = "asignaturas"
    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    facultad: Mapped[str] = mapped_column(String(150))
    creditos: Mapped[int] = mapped_column(Integer)


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), default="", server_default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20), default=Rol.ESTUDIANTE.value, server_default="ESTUDIANTE")
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Vínculo necesario para que el rol DOCENTE vea únicamente sus propias métricas.
    profesor_id: Mapped[int | None] = mapped_column(ForeignKey("profesores.id"), nullable=True)


class Oferta(Base):
    __tablename__ = "ofertas"
    __table_args__ = (UniqueConstraint("profesor_id", "asignatura_codigo", "periodo", "seccion", name="uq_oferta"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    profesor_id: Mapped[int] = mapped_column(ForeignKey("profesores.id"))
    asignatura_codigo: Mapped[str] = mapped_column(ForeignKey("asignaturas.codigo"))
    periodo: Mapped[str] = mapped_column(String(10))
    seccion: Mapped[str] = mapped_column(String(10))
    profesor: Mapped["Profesor"] = relationship(lazy="joined")
    asignatura: Mapped["Asignatura"] = relationship(lazy="joined")


class Resena(Base):
    """Sujeto del patrón Observer: notifica a sus observadores al recibir un reporte."""

    __tablename__ = "resenas"
    __table_args__ = (UniqueConstraint("autor_hash", "oferta_id", name="uq_resena_autor_oferta"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    oferta_id: Mapped[int] = mapped_column(ForeignKey("ofertas.id"), index=True)
    autor_hash: Mapped[str] = mapped_column(String(64), index=True)
    claridad: Mapped[int] = mapped_column(SmallInteger)
    exigencia: Mapped[int] = mapped_column(SmallInteger)
    puntualidad: Mapped[int] = mapped_column(SmallInteger)
    recomienda: Mapped[bool] = mapped_column(Boolean)
    comentario: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(40)), default=list, server_default="{}")
    estado: Mapped[str] = mapped_column(String(20), default=EstadoResena.VISIBLE.value, server_default="visible")
    creada: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    oferta: Mapped["Oferta"] = relationship(lazy="joined")
    reportes: Mapped[list["Reporte"]] = relationship(cascade="all, delete-orphan", passive_deletes=True)
    votos: Mapped[list["VotoUtilidad"]] = relationship(cascade="all, delete-orphan", passive_deletes=True)

    # --- Observer ---
    def suscribir(self, observador) -> None:
        if not hasattr(self, "_observadores"):
            self._observadores = []
        self._observadores.append(observador)

    def notificar_reporte(self) -> None:
        for o in getattr(self, "_observadores", []):
            o.actualizar(self)


class Reporte(Base):
    __tablename__ = "reportes"
    resena_id: Mapped[int] = mapped_column(
        ForeignKey("resenas.id", ondelete="CASCADE"), primary_key=True, autoincrement=False
    )
    reportante_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    motivo: Mapped[str] = mapped_column(String(300))


class VotoUtilidad(Base):
    __tablename__ = "votos_utilidad"
    resena_id: Mapped[int] = mapped_column(
        ForeignKey("resenas.id", ondelete="CASCADE"), primary_key=True, autoincrement=False
    )
    usuario_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    es_util: Mapped[bool] = mapped_column(Boolean)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    accion: Mapped[str] = mapped_column(String(200))
    ejecutado_por: Mapped[str] = mapped_column(String(255))
