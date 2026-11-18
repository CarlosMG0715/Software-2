from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from .models import TAGS_PREDEFINIDOS


class RegistroIn(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=8, max_length=72)
    acepta_ley_1581: bool


class TokenIn(BaseModel):
    token: str = Field(min_length=10)


class LoginIn(BaseModel):
    correo: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class RecuperarIn(BaseModel):
    correo: str | None = Field(default=None, max_length=255)
    token: str | None = None
    nueva_password: str | None = Field(default=None, min_length=8, max_length=72)

    @model_validator(mode="after")
    def _uno_u_otro(self):
        if self.token:
            if not self.nueva_password:
                raise ValueError("Ingresa la nueva contraseña.")
        elif not self.correo:
            raise ValueError("Ingresa tu correo para recibir el token.")
        return self


class ResenaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    claridad: int = Field(ge=1, le=5)
    exigencia: int = Field(ge=1, le=5)
    puntualidad: int = Field(ge=1, le=5)
    recomienda: bool
    comentario: str = Field(min_length=30, max_length=1000)
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def _tags_validos(cls, v: list[str]) -> list[str]:
        invalidos = [t for t in v if t not in TAGS_PREDEFINIDOS]
        if invalidos:
            raise ValueError("Etiqueta no permitida: " + ", ".join(invalidos))
        return list(dict.fromkeys(v))


class ResenaCrear(ResenaBase):
    oferta_id: int


class ResenaEditar(ResenaBase):
    pass


class VotoIn(BaseModel):
    es_util: bool


class ReporteIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    motivo: str = Field(min_length=3, max_length=300)