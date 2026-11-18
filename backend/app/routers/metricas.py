from fastapi import APIRouter, Depends, Response

from ..deps import get_metricas_service, requiere_roles
from ..models import Rol, Usuario
from ..services.metricas_service import MetricasService

router = APIRouter(prefix="/metricas", tags=["métricas"])
docente = requiere_roles(Rol.DOCENTE)


@router.get("/docente")
def metricas(u: Usuario = Depends(docente), s: MetricasService = Depends(get_metricas_service)):
    return s.docente(u)


@router.get("/docente/pdf")
def metricas_pdf(u: Usuario = Depends(docente), s: MetricasService = Depends(get_metricas_service)):
    return Response(
        content=s.pdf(u),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="metricas-docente.pdf"'},
    )