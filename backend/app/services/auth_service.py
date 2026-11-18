import logging
import math
from datetime import datetime, timedelta, timezone

from ..config import settings
from ..errors import AppError
from ..models import Rol, Usuario
from ..repositories.interfaces import ConflictoError
from ..repositories.sql import SqlAuditRepository, SqlUsuarioRepository
from ..security import crear_token, hash_password, huella, leer_token, verificar_password

logger = logging.getLogger("uvicorn.error")


class AuthService:
    def __init__(self, usuarios: SqlUsuarioRepository, auditoria: SqlAuditRepository):
        self.usuarios = usuarios
        self.auditoria = auditoria

    def _enviar_token(self, correo: str, asunto: str, token: str) -> dict:
        logger.info("[CORREO SIMULADO] Para: %s | %s | token: %s", correo, asunto, token)
        resp: dict = {}
        if settings.mostrar_token_en_respuesta:
            resp["token_dev"] = token
        return resp

    def registrar(self, correo: str, password: str, acepta_ley: bool) -> dict:
        correo = correo.strip().lower()
        if not acepta_ley:
            raise AppError(422, "Debes aceptar el tratamiento de datos personales (Ley 1581 de 2012).", "acepta_ley_1581")
        if correo.rsplit("@", 1)[-1] != settings.dominio_institucional.lower():
            raise AppError(422, f"Solo se permiten correos institucionales (@{settings.dominio_institucional}).", "correo")
        if self.usuarios.buscar_por_correo(correo):
            raise AppError(409, "Ya existe una cuenta con ese correo.", "correo")
        usuario = Usuario(correo=correo, password_hash=hash_password(password), verificado=False, rol=Rol.ESTUDIANTE.value)
        try:
            self.usuarios.guardar(usuario)
        except ConflictoError:
            raise AppError(409, "Ya existe una cuenta con ese correo.", "correo")
        self.auditoria.registrar("ACEPTACION_LEY_1581", f"usuario:{usuario.id}")
        token = crear_token(usuario.id, "activacion", settings.token_temporal_minutes)
        return {"mensaje": "Cuenta creada. Ingresa el token de activación enviado a tu correo.",
                **self._enviar_token(correo, "Activa tu cuenta", token)}

    def verificar_token(self, token: str) -> dict:
        payload = leer_token(token, "activacion")
        usuario = self.usuarios.buscar_por_id(int(payload["sub"]))
        if not usuario:
            raise AppError(400, "Token inválido.", "token")
        usuario.verificado = True
        self.usuarios.guardar(usuario)
        return {"mensaje": "Cuenta activada. Ya puedes iniciar sesión."}

    def login(self, correo: str, password: str) -> dict:
        usuario = self.usuarios.buscar_por_correo(correo.strip().lower())
        ahora = datetime.now(timezone.utc)
        if usuario and usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            minutos = max(1, math.ceil((usuario.bloqueado_hasta - ahora).total_seconds() / 60))
            raise AppError(423, f"Cuenta bloqueada temporalmente por intentos fallidos. Intenta de nuevo en {minutos} min.")
        if not usuario or not verificar_password(password, usuario.password_hash):
            if usuario:
                usuario.intentos_fallidos += 1
                if usuario.intentos_fallidos >= settings.max_intentos:
                    usuario.bloqueado_hasta = ahora + timedelta(minutes=settings.minutos_bloqueo)
                    usuario.intentos_fallidos = 0
                self.usuarios.guardar(usuario)
            raise AppError(401, "Correo o contraseña incorrectos.")
        if not usuario.verificado:
            raise AppError(403, "Debes activar tu cuenta con el token enviado a tu correo.")
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        self.usuarios.guardar(usuario)
        token = crear_token(usuario.id, "acceso", settings.access_token_minutes)
        return {"access_token": token, "token_type": "bearer", "rol": usuario.rol, "correo": usuario.correo}

    def recuperar_clave(self, correo: str | None, token: str | None, nueva_password: str | None) -> dict:
        if token:
            payload = leer_token(token, "recuperacion")
            usuario = self.usuarios.buscar_por_id(int(payload["sub"]))
            if not usuario or payload.get("fp") != huella(usuario.password_hash):
                raise AppError(400, "Este token ya fue utilizado o no es válido.", "token")
            usuario.password_hash = hash_password(nueva_password or "")
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            self.usuarios.guardar(usuario)
            return {"mensaje": "Contraseña actualizada. Ya puedes iniciar sesión."}
        usuario = self.usuarios.buscar_por_correo((correo or "").strip().lower())
        resp = {"mensaje": "Si el correo está registrado, enviamos un token de recuperación."}
        if usuario:
            t = crear_token(usuario.id, "recuperacion", settings.token_temporal_minutes, fp=huella(usuario.password_hash))
            resp.update(self._enviar_token(usuario.correo, "Recupera tu clave", t))
        return resp