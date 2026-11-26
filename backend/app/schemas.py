from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from .models import TAGS_PREDEFINIDOS


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=72)
    acepta_ley_1581: bool


class LoginIn(BaseModel):
    correo: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class PerfilActualizarIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=2, max_length=150)
    correo: EmailStr


class PasswordCambiarIn(BaseModel):
    password: str = Field(min_length=8, max_length=72)
    repetir: str = Field(min_length=8, max_length=72)

    @model_validator(mode="after")
    def _coinciden(self):
        if self.password != self.repetir:
            raise ValueError("Las contraseñas no coinciden.")
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
