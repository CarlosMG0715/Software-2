from typing import Sequence

from ..models import Resena
from ..repositories.interfaces import IResenaRepository


def resena_a_dict(r: Resena, votos: tuple[int, int] = (0, 0), incluir_estado: bool = False) -> dict:
    """Representación pública: jamás incluye autor_hash."""
    d = {
        "id": r.id,
        "oferta_id": r.oferta_id,
        "profesor_id": r.oferta.profesor_id,
        "profesor_nombre": r.oferta.profesor.nombre,
        "asignatura_codigo": r.oferta.asignatura_codigo,
        "asignatura_nombre": r.oferta.asignatura.nombre,
        "periodo": r.oferta.periodo,
        "claridad": r.claridad,
        "exigencia": r.exigencia,
        "puntualidad": r.puntualidad,
        "recomienda": r.recomienda,
        "comentario": r.comentario,
        "tags": list(r.tags or []),
        "creada": r.creada,
        "utiles": votos[0],
        "no_utiles": votos[1],
    }
    if incluir_estado:
        d["estado"] = r.estado
    return d


def serializar_lista(repo: IResenaRepository, resenas: Sequence[Resena], incluir_estado: bool = False) -> list[dict]:
    resumen = repo.votos_resumen([r.id for r in resenas])
    return [resena_a_dict(r, resumen.get(r.id, (0, 0)), incluir_estado) for r in resenas]