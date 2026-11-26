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


def hash_seudonimo(usuario_id: int) -> str:
    """Seudonimiza el ID con una clave privada del servidor, no con el HASH_SALT heredado."""
    mensaje = f"resena:autor:usuario:{usuario_id}".encode()
    return hmac.new(settings.secret_key.encode(), mensaje, hashlib.sha256).hexdigest()


def hash_ip(ip: str) -> str:
    """Evita almacenar direcciones IP en claro en los contadores de intentos."""
    return hmac.new(settings.secret_key.encode(), ip.encode(), hashlib.sha256).hexdigest()


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
