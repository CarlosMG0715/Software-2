import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("uvicorn.error")


class AppError(Exception):
    def __init__(self, status: int, mensaje: str, campo: str | None = None):
        self.status = status
        self.mensaje = mensaje
        self.campo = campo


def _traducir(err: dict) -> str:
    tipo = err.get("type", "")
    ctx = err.get("ctx") or {}
    msg = str(err.get("msg", ""))
    if tipo == "missing":
        return "Este campo es obligatorio."
    if tipo == "string_too_short":
        return f"Debe tener al menos {ctx.get('min_length')} caracteres."
    if tipo == "string_too_long":
        return f"No puede superar {ctx.get('max_length')} caracteres."
    if tipo in ("greater_than_equal", "less_than_equal", "greater_than", "less_than"):
        return "El valor está fuera del rango permitido."
    if tipo in ("int_parsing", "int_type", "float_parsing", "float_type"):
        return "Debe ser un número válido."
    if tipo in ("bool_parsing", "bool_type"):
        return "Debe ser verdadero o falso."
    if tipo == "value_error":
        if "email" in msg.lower():
            return "Correo electrónico inválido."
        return msg.replace("Value error, ", "")
    return "Valor inválido."


def _campo(loc) -> str | None:
    nombres = [x for x in loc if isinstance(x, str) and x not in ("body", "query", "path")]
    return nombres[-1] if nombres else None


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError):
        cuerpo: dict = {"detail": exc.mensaje}
        if exc.campo:
            cuerpo["errores"] = [{"campo": exc.campo, "mensaje": exc.mensaje}]
        return JSONResponse(cuerpo, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def _validacion(request: Request, exc: RequestValidationError):
        errores = [{"campo": _campo(e["loc"]), "mensaje": _traducir(e)} for e in exc.errors()]
        return JSONResponse({"detail": "Revisa los datos ingresados.", "errores": errores}, status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        mensajes = {404: "Recurso no encontrado.", 405: "Método no permitido.", 401: "Debes iniciar sesión."}
        return JSONResponse({"detail": mensajes.get(exc.status_code, "Ocurrió un error.")}, status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def _inesperado(request: Request, exc: Exception):
        logger.exception("Error inesperado en %s %s", request.method, request.url.path)
        return JSONResponse({"detail": "Error interno del servidor."}, status_code=500)
