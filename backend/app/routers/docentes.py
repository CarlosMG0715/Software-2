from fastapi import APIRouter, Depends, Query

from ..deps import get_busqueda_service, get_consulta_service
from ..services.busqueda_service import BusquedaService
from ..services.consulta_service import ConsultaService

router = APIRouter(prefix="/docentes", tags=["docentes"])


@router.get("")
def buscar(
    q: str = Query("", max_length=100),
    tipo: str = "profesor",
    facultad: str | None = None,
    promedio_min: float | None = Query(None, ge=0, le=5),
    orden: str = "promedio_desc",
    s: BusquedaService = Depends(get_busqueda_service),
):
    return s.buscar(q, tipo, facultad, promedio_min, orden)


@router.get("/{docente_id}")
def detalle(docente_id: int, s: ConsultaService = Depends(get_consulta_service)):
    return s.detalle_docente(docente_id)