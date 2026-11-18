from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Asignatura, Profesor
from .interfaces import ConflictoError


class SqlCatalogoRepository:
    def __init__(self, db: Session):
        self.db = db

    def profesores(self) -> list[Profesor]:
        return list(self.db.scalars(select(Profesor).order_by(Profesor.nombre)))

    def asignaturas(self) -> list[Asignatura]:
        return list(self.db.scalars(select(Asignatura).order_by(Asignatura.codigo)))

    def buscar_profesor(self, profesor_id: int):
        return self.db.get(Profesor, profesor_id)

    def buscar_asignatura(self, codigo: str):
        return self.db.get(Asignatura, codigo)

    def guardar(self, obj):
        self.db.add(obj)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictoError()
        self.db.refresh(obj)
        return obj