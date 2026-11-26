from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .errors import AppError
from .models import Rol, Usuario
from .repositories.sql import SqlAuditRepository, SqlProfesorRepository, SqlResenaRepository, SqlUsuarioRepository
from .security import leer_token
from .services.auth_service import AuthService
from .services.busqueda_service import BusquedaService
from .services.consulta_service import ConsultaService
from .services.metricas_service import MetricasService
from .services.moderacion_service import ModeracionService
from .services.resena_service import ResenaService

_bearer = HTTPBearer(auto_error=False)


def usuario_actual(cred: HTTPAuthorizationCredentials | None = Depends(_bearer), db: Session = Depends(get_db)) -> Usuario:
    if not cred:
        raise AppError(401, "Debes iniciar sesión.")
    payload = leer_token(cred.credentials, "acceso", status=401, campo=None)
    usuario = db.get(Usuario, int(payload["sub"]))
    if not usuario or not usuario.verificado:
        raise AppError(401, "Tu sesión no es válida. Inicia sesión de nuevo.")
    return usuario


def requiere_roles(*roles: Rol):
    permitidos = {r.value for r in roles}

    def _dep(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in permitidos:
            raise AppError(403, "No tienes permisos para esta acción.")
        return usuario

    return _dep


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(SqlUsuarioRepository(db), SqlAuditRepository(db))


def get_busqueda_service(db: Session = Depends(get_db)) -> BusquedaService:
    return BusquedaService(SqlProfesorRepository(db))


def get_consulta_service(db: Session = Depends(get_db)) -> ConsultaService:
    return ConsultaService(SqlProfesorRepository(db), SqlResenaRepository(db))


def get_resena_service(db: Session = Depends(get_db)) -> ResenaService:
    repo, audit = SqlResenaRepository(db), SqlAuditRepository(db)
    return ResenaService(repo, SqlProfesorRepository(db), ModeracionService(repo, audit))


def get_moderacion_service(db: Session = Depends(get_db)) -> ModeracionService:
    return ModeracionService(SqlResenaRepository(db), SqlAuditRepository(db))


def get_metricas_service(db: Session = Depends(get_db)) -> MetricasService:
    return MetricasService(SqlProfesorRepository(db), SqlResenaRepository(db))