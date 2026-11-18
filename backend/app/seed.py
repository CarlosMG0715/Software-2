from sqlalchemy import func, select

from .config import settings
from .database import SessionLocal
from .models import Asignatura, Oferta, Profesor, Rol, Usuario
from .security import hash_password


def main() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(func.count(Profesor.id))) > 0:
            print("Seed omitido: ya existen datos.")
            return

        profes = [
            Profesor(nombre="Laura Martínez Ríos", departamento="Departamento de Matemáticas", facultad="Facultad de Ciencias"),
            Profesor(nombre="Andrés Felipe Gómez", departamento="Departamento de Sistemas", facultad="Facultad de Ingeniería"),
            Profesor(nombre="Camila Herrera Sánchez", departamento="Departamento de Física", facultad="Facultad de Ciencias"),
            Profesor(nombre="Jorge Iván Restrepo", departamento="Departamento de Electrónica", facultad="Facultad de Ingeniería"),
        ]
        db.add_all(profes)
        db.add_all([
            Asignatura(codigo="MAT101", nombre="Cálculo Diferencial", facultad="Facultad de Ciencias", creditos=4),
            Asignatura(codigo="SIS201", nombre="Estructuras de Datos", facultad="Facultad de Ingeniería", creditos=3),
            Asignatura(codigo="FIS102", nombre="Física Mecánica", facultad="Facultad de Ciencias", creditos=4),
            Asignatura(codigo="ELE301", nombre="Circuitos Eléctricos", facultad="Facultad de Ingeniería", creditos=3),
        ])
        db.flush()
        p1, p2, p3, p4 = (p.id for p in profes)
        db.add_all([
            Oferta(profesor_id=p1, asignatura_codigo="MAT101", periodo="2026-1", seccion="A"),
            Oferta(profesor_id=p1, asignatura_codigo="MAT101", periodo="2025-2", seccion="A"),
            Oferta(profesor_id=p2, asignatura_codigo="SIS201", periodo="2026-1", seccion="A"),
            Oferta(profesor_id=p2, asignatura_codigo="SIS201", periodo="2025-2", seccion="B"),
            Oferta(profesor_id=p3, asignatura_codigo="FIS102", periodo="2026-1", seccion="A"),
            Oferta(profesor_id=p3, asignatura_codigo="MAT101", periodo="2026-1", seccion="B"),
            Oferta(profesor_id=p4, asignatura_codigo="ELE301", periodo="2026-1", seccion="A"),
            Oferta(profesor_id=p4, asignatura_codigo="FIS102", periodo="2026-1", seccion="B"),
        ])
        dom = settings.dominio_institucional
        clave = hash_password("1234")
        db.add_all([
            Usuario(correo=f"estudiante@{dom}", password_hash=clave, verificado=True, rol=Rol.ESTUDIANTE.value),
            Usuario(correo=f"docente@{dom}", password_hash=clave, verificado=True, rol=Rol.DOCENTE.value, profesor_id=p1),
            Usuario(correo=f"moderador@{dom}", password_hash=clave, verificado=True, rol=Rol.MODERADOR.value),
            Usuario(correo=f"admin@{dom}", password_hash=clave, verificado=True, rol=Rol.ADMIN.value),
        ])
        db.commit()
        print("Seed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()