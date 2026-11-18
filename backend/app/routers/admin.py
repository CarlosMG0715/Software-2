from fastapi import APIRouter, Depends

from ..deps import get_admin_service, requiere_roles
from ..models import Rol, Usuario
from ..schemas_admin import AsignaturaIn, OfertaIn, ProfesorIn
from ..services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])
admin = requiere_roles(Rol.ADMIN)


@router.get("/catalogo")
def catalogo(_: Usuario = Depends(admin), s: AdminService = Depends(get_admin_service)):
    return s.listar()


@router.post("/profesores", status_code=201)
def crear_profesor(d: ProfesorIn, u: Usuario = Depends(admin), s: AdminService = Depends(get_admin_service)):
    return s.crear_profesor(u, d)


@router.post("/asignaturas", status_code=201)
def crear_asignatura(d: AsignaturaIn, u: Usuario = Depends(admin), s: AdminService = Depends(get_admin_service)):
    return s.crear_asignatura(u, d)


@router.post("/ofertas", status_code=201)
def crear_oferta(d: OfertaIn, u: Usuario = Depends(admin), s: AdminService = Depends(get_admin_service)):
    return s.crear_oferta(u, d)