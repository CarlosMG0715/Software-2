from fastapi import APIRouter, Depends

from ..deps import get_moderacion_service, requiere_roles
from ..models import Rol, Usuario
from ..services.moderacion_service import ModeracionService

router = APIRouter(prefix="/moderacion", tags=["moderación"])
moderador = requiere_roles(Rol.MODERADOR, Rol.ADMIN)


@router.get("/reportadas")
def reportadas(_: Usuario = Depends(moderador), s: ModeracionService = Depends(get_moderacion_service)):
    return s.reportadas()


@router.get("/auditoria")
def auditoria(_: Usuario = Depends(moderador), s: ModeracionService = Depends(get_moderacion_service)):
    return s.auditoria_lista()


@router.post("/{resena_id}/aprobar")
def aprobar(resena_id: int, u: Usuario = Depends(moderador), s: ModeracionService = Depends(get_moderacion_service)):
    return s.aprobar(u, resena_id)


@router.post("/{resena_id}/rechazar")
def rechazar(resena_id: int, u: Usuario = Depends(moderador), s: ModeracionService = Depends(get_moderacion_service)):
    return s.rechazar(u, resena_id)


@router.post("/{resena_id}/eliminar")
def eliminar(resena_id: int, u: Usuario = Depends(moderador), s: ModeracionService = Depends(get_moderacion_service)):
    return s.eliminar(u, resena_id)