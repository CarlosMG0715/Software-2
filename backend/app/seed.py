import random

from sqlalchemy import select

from .config import settings
from .database import SessionLocal
from .models import Asignatura, EstadoResena, Oferta, Profesor, Resena, Rol, TAGS_PREDEFINIDOS, Usuario
from .security import hash_seudonimo, hash_password


PROFESORES_INICIALES = [
    ("Laura Martínez Ríos", "Departamento de Matemáticas", "Facultad de Ciencias", "MAT101"),
    ("Andrés Felipe Gómez", "Departamento de Sistemas", "Facultad de Ingeniería", "SIS201"),
    ("Camila Herrera Sánchez", "Departamento de Física", "Facultad de Ciencias", "FIS102"),
    ("Jorge Iván Restrepo", "Departamento de Electrónica", "Facultad de Ingeniería", "ELE301"),
]

NOMBRES_DOCENTES = ["Natalia", "David", "Manuela", "Santiago", "Sara", "Tomás", "Gabriela", "Sebastián", "Mariana", "Felipe"]
APELLIDOS_DOCENTES = ["Ospina Vélez", "Pardo Salazar", "Castaño Muñoz"]
NOMBRES_ADICIONALES = ["Juliana", "Esteban", "Lucía", "Emilio", "Paula", "Martín", "Daniela", "Joaquín", "Antonia", "Simón"]
APELLIDO_ADICIONAL = "Quiroga Peña"
FACULTADES = ["Facultad de Ingeniería", "Facultad de Ciencias", "Facultad de Educación", "Facultad de Economía"]
DEPARTAMENTOS = ["Departamento de Sistemas", "Departamento de Matemáticas", "Departamento de Educación", "Departamento de Economía", "Departamento de Física"]
ASIGNATURAS_DEMO = [
    "Analítica de Datos", "Arquitectura de Software", "Métodos de Investigación", "Estadística Aplicada",
    "Diseño de Productos", "Gestión de Proyectos", "Biología General", "Economía Pública",
    "Comunicación Digital", "Programación Avanzada",
]
COMENTARIOS_DEMO = [
    "Las explicaciones fueron claras y cada tema se acompañó con ejemplos útiles para practicar por cuenta propia.",
    "El curso estuvo bien organizado; las actividades ayudaron a relacionar la teoría con situaciones reales.",
    "Hubo buen material de apoyo y las clases permitieron resolver dudas antes de cada evaluación.",
    "La materia exige constancia, pero los objetivos y criterios de evaluación se comunicaron con claridad.",
]


def _profesor_por_nombre(db, nombre: str) -> Profesor | None:
    return db.scalar(select(Profesor).where(Profesor.nombre == nombre))


def _asegurar_asignatura(db, codigo: str, nombre: str, facultad: str) -> None:
    if db.get(Asignatura, codigo) is None:
        db.add(Asignatura(codigo=codigo, nombre=nombre, facultad=facultad, creditos=3))


def _asegurar_oferta(db, profesor_id: int, codigo: str) -> Oferta:
    oferta = db.scalar(select(Oferta).where(
        Oferta.profesor_id == profesor_id,
        Oferta.asignatura_codigo == codigo,
        Oferta.periodo == "2026-1",
        Oferta.seccion == "A",
    ))
    if oferta is None:
        oferta = Oferta(profesor_id=profesor_id, asignatura_codigo=codigo, periodo="2026-1", seccion="A")
        db.add(oferta)
        db.flush()
    return oferta


def _estudiantes_demo(db, dominio: str) -> list[Usuario]:
    clave = hash_password("Estudiante123!")
    estudiantes = []
    for numero in range(1, 51):
        base = f"demo.estudiante{numero:02d}"
        correo = f"{base}@{dominio}"
        sufijo = 1
        usuario = db.scalar(select(Usuario).where(Usuario.correo == correo))
        while usuario is not None and usuario.rol != Rol.ESTUDIANTE.value:
            correo = f"{base}.{sufijo}@{dominio}"
            sufijo += 1
            usuario = db.scalar(select(Usuario).where(Usuario.correo == correo))
        if usuario is None:
            usuario = Usuario(
                nombre=f"Estudiante de Prueba {numero:02d}",
                correo=correo,
                password_hash=clave,
                rol=Rol.ESTUDIANTE.value,
            )
            db.add(usuario)
            db.flush()
        estudiantes.append(usuario)
    return estudiantes


def _valores_resena_demo(semilla: str) -> dict:
    azar = random.Random(semilla)
    cantidad_tags = azar.randint(0, 2)
    return {
        "claridad": azar.randint(1, 5),
        "exigencia": azar.randint(1, 5),
        "puntualidad": azar.randint(1, 5),
        "recomienda": azar.choice([True, False]),
        "comentario": azar.choice(COMENTARIOS_DEMO),
        "tags": azar.sample(TAGS_PREDEFINIDOS, cantidad_tags),
    }


def _asegurar_resenas_demo(db, oferta: Oferta, objetivo: int, estudiantes: list[Usuario]) -> None:
    estudiantes_por_hash = {hash_seudonimo(estudiante.id): estudiante for estudiante in estudiantes}
    hashes_demo = list(estudiantes_por_hash)
    existentes = list(db.scalars(select(Resena).where(
        Resena.oferta_id == oferta.id,
        Resena.autor_hash.in_(hashes_demo),
    )))
    autores_existentes = {resena.autor_hash for resena in existentes}

    # Randomize old sample reviews once using a stable seed so restarts do not change them.
    for resena in existentes:
        if resena.comentario in COMENTARIOS_DEMO:
            valores = _valores_resena_demo(f"demo-resena:{oferta.id}:{resena.autor_hash}")
            for campo, valor in valores.items():
                setattr(resena, campo, valor)

    faltantes = max(0, objetivo - len(existentes))
    disponibles = [estudiante for autor_hash, estudiante in estudiantes_por_hash.items() if autor_hash not in autores_existentes]
    azar = random.Random(f"demo-autores:{oferta.id}")
    seleccionados = azar.sample(disponibles, min(faltantes, len(disponibles)))
    for estudiante in seleccionados:
        autor_hash = hash_seudonimo(estudiante.id)
        valores = _valores_resena_demo(f"demo-resena:{oferta.id}:{autor_hash}")
        db.add(Resena(
            oferta_id=oferta.id,
            autor_hash=autor_hash,
            estado=EstadoResena.VISIBLE.value,
            **valores,
        ))


def main() -> None:
    db = SessionLocal()
    try:
        dominio = settings.dominio_institucional
        profesores_base = []
        ofertas_base = []

        # Keep the original four sample teachers and their subjects if already present.
        for nombre, departamento, facultad, codigo in PROFESORES_INICIALES:
            profesor = _profesor_por_nombre(db, nombre)
            if profesor is None:
                profesor = Profesor(nombre=nombre, departamento=departamento, facultad=facultad)
                db.add(profesor)
                db.flush()
            _asegurar_asignatura(db, codigo, {
                "MAT101": "Cálculo Diferencial", "SIS201": "Estructuras de Datos",
                "FIS102": "Física Mecánica", "ELE301": "Circuitos Eléctricos",
            }[codigo], facultad)
            profesores_base.append(profesor)
            ofertas_base.append(_asegurar_oferta(db, profesor.id, codigo))

        # Add 30 standard demo teachers and 10 extra home-page teachers.
        profesores_nuevos = []
        ofertas_nuevas = []
        for numero in range(40):
            if numero < 30:
                nombre = f"{NOMBRES_DOCENTES[numero % 10]} {APELLIDOS_DOCENTES[numero // 10]}"
            else:
                nombre = f"{NOMBRES_ADICIONALES[numero - 30]} {APELLIDO_ADICIONAL}"
            facultad = FACULTADES[numero % len(FACULTADES)]
            departamento = DEPARTAMENTOS[numero % len(DEPARTAMENTOS)]
            codigo = f"PRB{numero + 1:03d}"
            profesor = _profesor_por_nombre(db, nombre)
            if profesor is None:
                profesor = Profesor(nombre=nombre, departamento=departamento, facultad=facultad)
                db.add(profesor)
                db.flush()
            _asegurar_asignatura(db, codigo, ASIGNATURAS_DEMO[numero % len(ASIGNATURAS_DEMO)], facultad)
            profesores_nuevos.append(profesor)
            ofertas_nuevas.append(_asegurar_oferta(db, profesor.id, codigo))

        # Preserve the familiar seed accounts and add fifty reusable student accounts.
        clave_demo = hash_password("1234")
        cuenta_estudiante = db.scalar(select(Usuario).where(Usuario.correo == f"estudiante@{dominio}"))
        if cuenta_estudiante is None:
            cuenta_estudiante = Usuario(correo=f"estudiante@{dominio}", password_hash=clave_demo, rol=Rol.ESTUDIANTE.value)
            db.add(cuenta_estudiante)
        if db.scalar(select(Usuario).where(Usuario.correo == f"docente@{dominio}")) is None:
            db.add(Usuario(correo=f"docente@{dominio}", password_hash=clave_demo, rol=Rol.DOCENTE.value, profesor_id=profesores_base[0].id))
        for rol, correo in ((Rol.MODERADOR, f"moderador@{dominio}"), (Rol.ADMIN, f"admin@{dominio}")):
            if db.scalar(select(Usuario).where(Usuario.correo == correo)) is None:
                db.add(Usuario(correo=correo, password_hash=clave_demo, rol=rol.value))
        estudiantes = _estudiantes_demo(db, dominio)
        db.flush()

        # Every sample teacher gets a random student review; extra teachers get ten each.
        for oferta in ofertas_base:
            _asegurar_resenas_demo(db, oferta, 1, estudiantes)
        for numero, oferta in enumerate(ofertas_nuevas):
            _asegurar_resenas_demo(db, oferta, 1 if numero < 30 else 10, estudiantes)

        db.commit()
        print("Seed listo: 30 docentes demo, 10 adicionales y 50 estudiantes demo con reseñas de prueba.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
