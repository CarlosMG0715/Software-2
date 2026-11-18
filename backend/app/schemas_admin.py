from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ProfesorIn(_Base):
    nombre: str = Field(min_length=3, max_length=150)
    departamento: str = Field(min_length=3, max_length=150)
    facultad: str = Field(min_length=3, max_length=150)


class AsignaturaIn(_Base):
    codigo: str = Field(min_length=3, max_length=20)
    nombre: str = Field(min_length=3, max_length=150)
    facultad: str = Field(min_length=3, max_length=150)
    creditos: int = Field(ge=1, le=12)


class OfertaIn(_Base):
    profesor_id: int
    asignatura_codigo: str = Field(min_length=3, max_length=20)
    periodo: str = Field(pattern=r"^\d{4}-[12]$")
    seccion: str = Field(min_length=1, max_length=10)