from fastapi import APIRouter, Depends

from ..deps import get_consulta_service
from ..services.consulta_service import ConsultaService

router = APIRouter(prefix="/asignaturas", tags=["asignaturas"])


@router.get("/{codigo}")
def detalle(codigo: str, s: ConsultaService = Depends(get_consulta_service)):
    return s.detalle_asignatura(codigo)