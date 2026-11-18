from abc import ABC, abstractmethod

from sqlalchemy import select

from ..errors import AppError
from ..models import Asignatura, Oferta, Profesor
from ..repositories.interfaces import IProfesorRepository


def _like(q: str) -> str:
    return "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


class EstrategiaBusqueda(ABC):
    """Strategy: cada estrategia produce un criterio SQL sobre Profesor."""

    @abstractmethod
    def criterio(self, q: str): ...


class BusquedaPorProfesor(EstrategiaBusqueda):
    def criterio(self, q: str):
        return Profesor.nombre.ilike(_like(q), escape="\\")


class BusquedaPorCodigo(EstrategiaBusqueda):
    def criterio(self, q: str):
        sub = select(Oferta.profesor_id).where(Oferta.asignatura_codigo.ilike(_like(q), escape="\\"))
        return Profesor.id.in_(sub)


class BusquedaPorMateria(EstrategiaBusqueda):
    def criterio(self, q: str):
        sub = (
            select(Oferta.profesor_id)
            .join(Asignatura, Asignatura.codigo == Oferta.asignatura_codigo)
            .where(Asignatura.nombre.ilike(_like(q), escape="\\"))
        )
        return Profesor.id.in_(sub)


ORDENES = ("promedio_desc", "promedio_asc", "nombre", "resenas")


class BusquedaService:
    def __init__(self, profesores: IProfesorRepository):
        self.profesores = profesores
        self.estrategias: dict[str, EstrategiaBusqueda] = {
            "profesor": BusquedaPorProfesor(),
            "codigo": BusquedaPorCodigo(),
            "materia": BusquedaPorMateria(),
        }

    def buscar(self, q: str, tipo: str, facultad: str | None, promedio_min: float | None, orden: str) -> list[dict]:
        estrategia = self.estrategias.get(tipo)
        if not estrategia:
            raise AppError(422, "Tipo de búsqueda no válido (profesor, codigo o materia).", "tipo")
        if orden not in ORDENES:
            raise AppError(422, "Orden no válido.", "orden")
        criterios = []
        if q.strip():
            criterios.append(estrategia.criterio(q.strip()))
        if facultad:
            criterios.append(Profesor.facultad == facultad)
        profesores = self.profesores.listar(criterios)
        stats = self.profesores.estadisticas([p.id for p in profesores])
        items = []
        for p in profesores:
            s = stats.get(p.id)
            items.append({
                "id": p.id, "nombre": p.nombre, "departamento": p.departamento, "facultad": p.facultad,
                "promedio": s["promedio"] if s else None,
                "total_resenas": s["total"] if s else 0,
                "pct_recomienda": s["pct_recomienda"] if s else None,
            })
        if promedio_min is not None:
            items = [i for i in items if i["promedio"] is not None and i["promedio"] >= promedio_min]
        if orden == "promedio_asc":
            items.sort(key=lambda i: (i["promedio"] is None, i["promedio"] or 0))
        elif orden == "resenas":
            items.sort(key=lambda i: -i["total_resenas"])
        elif orden == "promedio_desc":
            items.sort(key=lambda i: (i["promedio"] is None, -(i["promedio"] or 0)))
        return items