from ..errors import AppError
from ..repositories.interfaces import IProfesorRepository, IResenaRepository
from .metricas_service import calcular_metricas
from .serializadores import serializar_lista


class ConsultaService:
    def __init__(self, profesores: IProfesorRepository, resenas: IResenaRepository):
        self.profesores = profesores
        self.resenas = resenas

    def detalle_docente(self, profesor_id: int) -> dict:
        p = self.profesores.buscar_por_id(profesor_id)
        if not p:
            raise AppError(404, "El docente no existe.")
        publicas = self.resenas.buscar_por_profesor(profesor_id)
        m = calcular_metricas(publicas)
        return {
            "docente": {"id": p.id, "nombre": p.nombre, "departamento": p.departamento, "facultad": p.facultad},
            "promedios": m["promedios"],
            "pct_recomienda": m["pct_recomienda"],
            "total_resenas": m["total"],
            "resenas": serializar_lista(self.resenas, publicas),
            "ofertas": [
                {"id": o.id, "asignatura_codigo": o.asignatura_codigo, "asignatura_nombre": o.asignatura.nombre,
                 "periodo": o.periodo, "seccion": o.seccion}
                for o in self.profesores.ofertas_de(profesor_id)
            ],
        }

    def detalle_asignatura(self, codigo: str) -> dict:
        a = self.profesores.buscar_asignatura(codigo.upper())
        if not a:
            raise AppError(404, "La asignatura no existe.")
        docentes: dict[int, dict] = {}
        for pid, nombre, periodo, prom, total in self.profesores.promedios_por_asignatura(a.codigo):
            d = docentes.setdefault(pid, {"profesor_id": pid, "nombre": nombre, "periodos": []})
            d["periodos"].append({"periodo": periodo, "promedio": round(float(prom), 2) if prom is not None else None,
                                  "total_resenas": total})
        return {
            "asignatura": {"codigo": a.codigo, "nombre": a.nombre, "facultad": a.facultad, "creditos": a.creditos},
            "docentes": list(docentes.values()),
        }