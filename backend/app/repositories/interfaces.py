from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence

from ..models import Asignatura, Oferta, Profesor, Reporte, Resena, VotoUtilidad


class ConflictoError(Exception):
    """Violación de unicidad (voto, reporte o reseña duplicados)."""


class IResenaRepository(ABC):
    @abstractmethod
    def guardar(self, resena: Resena) -> Resena: ...

    @abstractmethod
    def buscar_por_oferta(self, oferta_id: int, solo_publicas: bool = True) -> list[Resena]: ...

    @abstractmethod
    def eliminar(self, resena: Resena) -> None: ...

    # --- consultas de apoyo ---
    @abstractmethod
    def buscar_por_id(self, resena_id: int) -> Optional[Resena]: ...

    @abstractmethod
    def buscar_por_autor(self, autor_hash: str) -> list[Resena]: ...

    @abstractmethod
    def buscar_por_profesor(self, profesor_id: int, solo_publicas: bool = True) -> list[Resena]: ...

    @abstractmethod
    def existe_para_autor(self, autor_hash: str, profesor_id: int, asignatura_codigo: str, periodo: str) -> bool: ...

    @abstractmethod
    def votos_resumen(self, ids: Sequence[int]) -> dict[int, tuple[int, int]]: ...

    @abstractmethod
    def existe_voto(self, resena_id: int, usuario_hash: str) -> bool: ...

    @abstractmethod
    def agregar_voto(self, voto: VotoUtilidad) -> None: ...

    @abstractmethod
    def existe_reporte(self, resena_id: int, reportante_hash: str) -> bool: ...

    @abstractmethod
    def agregar_reporte(self, reporte: Reporte) -> None: ...

    @abstractmethod
    def limpiar_reportes(self, resena_id: int) -> None: ...

    @abstractmethod
    def reportes_de(self, ids: Sequence[int]) -> dict[int, list[str]]: ...

    @abstractmethod
    def cola_moderacion(self) -> list[Resena]: ...


class IProfesorRepository(ABC):
    @abstractmethod
    def buscar_por_id(self, profesor_id: int) -> Optional[Profesor]: ...

    @abstractmethod
    def listar(self, criterios: Optional[Sequence[Any]] = None) -> list[Profesor]: ...

    # --- consultas de apoyo ---
    @abstractmethod
    def estadisticas(self, ids: Sequence[int]) -> dict[int, dict]: ...

    @abstractmethod
    def buscar_oferta(self, oferta_id: int) -> Optional[Oferta]: ...

    @abstractmethod
    def ofertas_de(self, profesor_id: int) -> list[Oferta]: ...

    @abstractmethod
    def buscar_asignatura(self, codigo: str) -> Optional[Asignatura]: ...

    @abstractmethod
    def promedios_por_asignatura(self, codigo: str) -> list[Any]: ...
