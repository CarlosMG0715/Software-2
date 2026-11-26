import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings
from .errors import AppError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], password_hash.encode())
    except ValueError:
        return False


def hash_anonimo(usuario_id: int) -> str:
    """Identificador irreversible del autor (HMAC con sal secreta). Nunca se expone."""
    return hmac.new(settings.hash_salt.encode(), f"usuario:{usuario_id}".encode(), hashlib.sha256).hexdigest()


def crear_token(sub: int, proposito: str, minutos: int, **extra) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {"sub": str(sub), "prp": proposito, "iat": ahora, "exp": ahora + timedelta(minutes=minutos), **extra}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def leer_token(token: str, proposito: str, status: int = 400, campo: str | None = "token") -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AppError(status, "El token expiró. Solicita uno nuevo.", campo)
    except jwt.PyJWTError:
        raise AppError(status, "Token inválido.", campo)
    if payload.get("prp") != proposito:
        raise AppError(status, "Token inválido.", campo)
    return payload
