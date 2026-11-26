from fastapi import APIRouter, Depends

from ..deps import get_auth_service, usuario_actual
from ..models import Usuario
from ..schemas import LoginIn, PasswordCambiarIn, PerfilActualizarIn, RegistroIn
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registrar", status_code=201)
def registrar(datos: RegistroIn, s: AuthService = Depends(get_auth_service)):
    return s.registrar(datos.nombre, datos.correo, datos.password, datos.acepta_ley_1581)


@router.post("/login")
def login(datos: LoginIn, s: AuthService = Depends(get_auth_service)):
    return s.login(datos.correo, datos.password)


@router.patch("/perfil")
def actualizar_perfil(
    datos: PerfilActualizarIn,
    u: Usuario = Depends(usuario_actual),
    s: AuthService = Depends(get_auth_service),
):
    return s.actualizar_perfil(u, datos.nombre, str(datos.correo))


@router.put("/perfil/password")
def cambiar_password(
    datos: PasswordCambiarIn,
    u: Usuario = Depends(usuario_actual),
    s: AuthService = Depends(get_auth_service),
):
    return s.cambiar_password(u, datos.password)
