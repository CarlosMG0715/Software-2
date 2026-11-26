from datetime import datetime, timezone

from ..config import settings
from ..errors import AppError
from ..models import Rol, Usuario
from ..repositories.interfaces import ConflictoError
from ..repositories.sql import SqlAuditRepository, SqlLoginRateLimitRepository, SqlUsuarioRepository
from ..security import crear_token, hash_ip, hash_password, verificar_password


class AuthService:
    def __init__(
        self,
        usuarios: SqlUsuarioRepository,
        auditoria: SqlAuditRepository,
        limites_login: SqlLoginRateLimitRepository,
    ):
        self.usuarios = usuarios
        self.auditoria = auditoria
        self.limites_login = limites_login

    def registrar(self, nombre: str, correo: str, password: str, acepta_ley: bool) -> dict:
        nombre = nombre.strip()
        if len(nombre) < 2:
            raise AppError(422, "Ingresa tu nombre.", "nombre")
        correo = correo.strip().lower()
        if not acepta_ley:
            raise AppError(422, "Debes aceptar el tratamiento de datos personales (Ley 1581 de 2012).", "acepta_ley_1581")
        if correo.rsplit("@", 1)[-1] != settings.dominio_institucional.lower():
            raise AppError(422, f"Solo se permiten correos institucionales (@{settings.dominio_institucional}).", "correo")
        if self.usuarios.buscar_por_correo(correo):
            raise AppError(409, "Ya existe una cuenta con ese correo.", "correo")
        usuario = Usuario(nombre=nombre, correo=correo, password_hash=hash_password(password), rol=Rol.ESTUDIANTE.value)
        try:
            self.usuarios.guardar(usuario)
        except ConflictoError:
            raise AppError(409, "Ya existe una cuenta con ese correo.", "correo")
        self.auditoria.registrar("ACEPTACION_LEY_1581", f"usuario:{usuario.id}")
        return {"mensaje": "Cuenta creada. Bienvenido/a.", **self._crear_sesion(usuario)}

    def login(self, correo: str, password: str, ip_cliente: str) -> dict:
        ahora = datetime.now(timezone.utc)
        segundos_ventana = settings.login_ventana_minutos * 60
        inicio_ventana = datetime.fromtimestamp(
            int(ahora.timestamp()) // segundos_ventana * segundos_ventana,
            tz=timezone.utc,
        )
        intentos = self.limites_login.registrar_intento(hash_ip(ip_cliente), inicio_ventana)
        if intentos > settings.login_max_intentos_por_ip:
            raise AppError(429, "Demasiados intentos desde esta conexión. Intenta de nuevo más tarde.")

        usuario = self.usuarios.buscar_por_correo(correo.strip().lower())
        if not usuario or not verificar_password(password, usuario.password_hash):
            raise AppError(401, "Correo o contraseña incorrectos.")
        return self._crear_sesion(usuario)

    def actualizar_perfil(self, usuario: Usuario, nombre: str, correo: str) -> dict:
        nombre = nombre.strip()
        correo = correo.strip().lower()
        if len(nombre) < 2:
            raise AppError(422, "Ingresa un nombre de usuario válido.", "nombre")
        if correo.rsplit("@", 1)[-1] != settings.dominio_institucional.lower():
            raise AppError(422, f"Solo se permiten correos institucionales (@{settings.dominio_institucional}).", "correo")
        existente = self.usuarios.buscar_por_correo(correo)
        if existente and existente.id != usuario.id:
            raise AppError(409, "Ya existe una cuenta con ese correo.", "correo")
        usuario.nombre = nombre
        usuario.correo = correo
        try:
            self.usuarios.guardar(usuario)
        except ConflictoError:
            raise AppError(409, "Ya existe una cuenta con ese correo.", "correo")
        self.auditoria.registrar("PERFIL_ACTUALIZADO", f"usuario:{usuario.id}")
        return {"mensaje": "Perfil actualizado.", "nombre": usuario.nombre, "correo": usuario.correo}

    def cambiar_password(self, usuario: Usuario, password: str) -> dict:
        usuario.password_hash = hash_password(password)
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        self.usuarios.guardar(usuario)
        self.auditoria.registrar("CLAVE_ACTUALIZADA", f"usuario:{usuario.id}")
        return {"mensaje": "Contraseña actualizada."}

    @staticmethod
    def _crear_sesion(usuario: Usuario) -> dict:
        token = crear_token(usuario.id, "acceso", settings.access_token_minutes)
        return {
            "access_token": token,
            "token_type": "bearer",
            "rol": usuario.rol,
            "correo": usuario.correo,
            "nombre": usuario.nombre,
        }

