from fastapi import APIRouter, Depends

from ..deps import get_auth_service
from ..schemas import LoginIn, RecuperarIn, RegistroIn, TokenIn
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registrar", status_code=201)
def registrar(datos: RegistroIn, s: AuthService = Depends(get_auth_service)):
    return s.registrar(datos.correo, datos.password, datos.acepta_ley_1581)


@router.post("/verificar-token")
def verificar_token(datos: TokenIn, s: AuthService = Depends(get_auth_service)):
    return s.verificar_token(datos.token)


@router.post("/login")
def login(datos: LoginIn, s: AuthService = Depends(get_auth_service)):
    return s.login(datos.correo, datos.password)


@router.post("/recuperar-clave")
def recuperar_clave(datos: RecuperarIn, s: AuthService = Depends(get_auth_service)):
    return s.recuperar_clave(datos.correo, datos.token, datos.nueva_password)