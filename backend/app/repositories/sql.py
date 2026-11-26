from typing import Any, Optional, Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, case, delete, exists, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import (
    ESTADOS_PUBLICOS, Asignatura, AuditLog, EstadoResena, LoginRateLimit, Oferta, Profesor, Reporte, Resena,
    Usuario, VotoUtilidad,
)
from .interfaces import ConflictoError, IProfesorRepository, IResenaRepository

_PROMEDIO = (Resena.claridad + Resena.exigencia + Resena.puntualidad) / 3.0


class SqlResenaRepository(IResenaRepository):
    def __init__(self, db: Session):
        self.db = db

    def guardar(self, resena: Resena) -> Resena:
        self.db.add(resena)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError()
        self.db.refresh(resena)
        return resena

    def buscar_por_oferta(self, oferta_id: int, solo_publicas: bool = True) -> list[Resena]:
        q = select(Resena).where(Resena.oferta_id == oferta_id)
        if solo_publicas:
            q = q.where(Resena.estado.in_(ESTADOS_PUBLICOS))
        return list(self.db.scalars(q.order_by(Resena.creada.desc())))

    def eliminar(self, resena: Resena) -> None:
        self.db.delete(resena)
        self.db.commit()

    def buscar_por_id(self, resena_id: int) -> Optional[Resena]:
        return self.db.get(Resena, resena_id)

    def buscar_por_autor(self, autor_hash: str) -> list[Resena]:
        q = select(Resena).where(Resena.autor_hash == autor_hash).order_by(Resena.creada.desc())
        return list(self.db.scalars(q))

    def buscar_por_profesor(self, profesor_id: int, solo_publicas: bool = True) -> list[Resena]:
        q = select(Resena).join(Oferta, Oferta.id == Resena.oferta_id).where(Oferta.profesor_id == profesor_id)
        if solo_publicas:
            q = q.where(Resena.estado.in_(ESTADOS_PUBLICOS))
        return list(self.db.scalars(q.order_by(Resena.creada.desc())))

    def existe_para_autor(self, autor_hash: str, profesor_id: int, asignatura_codigo: str, periodo: str) -> bool:
        q = (
            select(Resena.id)
            .join(Oferta, Oferta.id == Resena.oferta_id)
            .where(
                Resena.autor_hash == autor_hash,
                Oferta.profesor_id == profesor_id,
                Oferta.asignatura_codigo == asignatura_codigo,
                Oferta.periodo == periodo,
            )
            .limit(1)
        )
        return self.db.scalar(q) is not None

    def votos_resumen(self, ids: Sequence[int]) -> dict[int, tuple[int, int]]:
        if not ids:
            return {}
        q = (
            select(
                VotoUtilidad.resena_id,
                func.count().filter(VotoUtilidad.es_util),
                func.count().filter(~VotoUtilidad.es_util),
            )
            .where(VotoUtilidad.resena_id.in_(ids))
            .group_by(VotoUtilidad.resena_id)
        )
        return {rid: (u, n) for rid, u, n in self.db.execute(q)}

    def existe_voto(self, resena_id: int, usuario_hash: str) -> bool:
        return self.db.get(VotoUtilidad, (resena_id, usuario_hash)) is not None

    def agregar_voto(self, voto: VotoUtilidad) -> None:
        self.db.add(voto)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError()

    def existe_reporte(self, resena_id: int, reportante_hash: str) -> bool:
        return self.db.get(Reporte, (resena_id, reportante_hash)) is not None

    def agregar_reporte(self, reporte: Reporte) -> None:
        # Flush first so uniqueness conflicts can be converted to a domain error.
        self.db.add(reporte)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError()

    def limpiar_reportes(self, resena_id: int) -> None:
        self.db.execute(delete(Reporte).where(Reporte.resena_id == resena_id))

    def reportes_de(self, ids: Sequence[int]) -> dict[int, list[str]]:
        resultado: dict[int, list[str]] = {i: [] for i in ids}
        if ids:
            for rid, motivo in self.db.execute(select(Reporte.resena_id, Reporte.motivo).where(Reporte.resena_id.in_(ids))):
                resultado[rid].append(motivo)
        return resultado

    def cola_moderacion(self) -> list[Resena]:
        q = (
            select(Resena)
            .where(
                (Resena.estado == EstadoResena.PENDIENTE.value)
                | (
                    Resena.estado.in_([EstadoResena.VISIBLE.value, EstadoResena.APROBADA.value, EstadoResena.OCULTA.value])
                    & exists().where(Reporte.resena_id == Resena.id)
                ),
            )
            .order_by(Resena.creada.desc())
        )
        return list(self.db.scalars(q))


class SqlLoginRateLimitRepository:
    """Persists fixed-window login counters so limits apply across app workers."""

    def __init__(self, db: Session):
        self.db = db

    def registrar_intento(self, ip_hash: str, window_start: datetime) -> int:
        statement = pg_insert(LoginRateLimit).values(
            ip_hash=ip_hash, window_start=window_start, attempts=1
        )
        statement = statement.on_conflict_do_update(
            index_elements=[LoginRateLimit.ip_hash, LoginRateLimit.window_start],
            set_={"attempts": LoginRateLimit.attempts + 1},
        ).returning(LoginRateLimit.attempts)
        try:
            attempts = self.db.scalar(statement)
            self.db.execute(
                delete(LoginRateLimit).where(
                    LoginRateLimit.window_start < datetime.now(timezone.utc) - timedelta(days=1)
                )
            )
            self.db.commit()
            return int(attempts or 0)
        except Exception:
            self.db.rollback()
            raise


class SqlProfesorRepository(IProfesorRepository):
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, profesor_id: int) -> Optional[Profesor]:
        return self.db.get(Profesor, profesor_id)

    def listar(self, criterios: Optional[Sequence[Any]] = None) -> list[Profesor]:
        q = select(Profesor)
        for c in criterios or []:
            q = q.where(c)
        return list(self.db.scalars(q.order_by(Profesor.nombre)))

    def estadisticas(self, ids: Sequence[int]) -> dict[int, dict]:
        if not ids:
            return {}
        q = (
            select(
                Oferta.profesor_id,
                func.avg(_PROMEDIO),
                func.count(Resena.id),
                func.avg(case((Resena.recomienda, 1.0), else_=0.0)),
            )
            .join(Resena, Resena.oferta_id == Oferta.id)
            .where(Oferta.profesor_id.in_(ids), Resena.estado.in_(ESTADOS_PUBLICOS))
            .group_by(Oferta.profesor_id)
        )
        return {
            pid: {"promedio": round(float(prom), 2), "total": total, "pct_recomienda": round(float(rec) * 100, 1)}
            for pid, prom, total, rec in self.db.execute(q)
        }

    def buscar_oferta(self, oferta_id: int) -> Optional[Oferta]:
        return self.db.get(Oferta, oferta_id)

    def ofertas_de(self, profesor_id: int) -> list[Oferta]:
        q = select(Oferta).where(Oferta.profesor_id == profesor_id).order_by(Oferta.periodo.desc(), Oferta.asignatura_codigo)
        return list(self.db.scalars(q))

    def buscar_asignatura(self, codigo: str) -> Optional[Asignatura]:
        return self.db.get(Asignatura, codigo)

    def promedios_por_asignatura(self, codigo: str) -> list[Any]:
        q = (
            select(Profesor.id, Profesor.nombre, Oferta.periodo, func.avg(_PROMEDIO), func.count(Resena.id))
            .select_from(Oferta)
            .join(Profesor, Profesor.id == Oferta.profesor_id)
            .outerjoin(Resena, and_(Resena.oferta_id == Oferta.id, Resena.estado.in_(ESTADOS_PUBLICOS)))
            .where(Oferta.asignatura_codigo == codigo)
            .group_by(Profesor.id, Profesor.nombre, Oferta.periodo)
            .order_by(Profesor.nombre, Oferta.periodo.desc())
        )
        return list(self.db.execute(q))


class SqlUsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.get(Usuario, usuario_id)

    def buscar_por_correo(self, correo: str) -> Optional[Usuario]:
        return self.db.scalar(select(Usuario).where(Usuario.correo == correo))

    def guardar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError()
        self.db.refresh(usuario)
        return usuario


class SqlAuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar(self, accion: str, ejecutado_por: str, commit: bool = True) -> None:
        self.db.add(AuditLog(accion=accion, ejecutado_por=ejecutado_por))
        if commit:
            self.db.commit()

    def listar(self, limite: int = 200) -> list[AuditLog]:
        return list(self.db.scalars(select(AuditLog).order_by(AuditLog.fecha.desc(), AuditLog.id.desc()).limit(limite)))
