from ..errors import AppError
from ..models import Asignatura, Oferta, Profesor, Usuario
from ..repositories.catalogo import SqlCatalogoRepository
from ..repositories.interfaces import ConflictoError
from ..repositories.sql import SqlAuditRepository
from ..schemas_admin import AsignaturaIn, OfertaIn, ProfesorIn


class AdminService:
    def __init__(self, catalogo: SqlCatalogoRepository, auditoria: SqlAuditRepository):
        self.catalogo = catalogo
        self.auditoria = auditoria

    def listar(self) -> dict:
        profs, asigs = self.catalogo.profesores(), self.catalogo.asignaturas()
        return {
            "profesores": [{"id": p.id, "nombre": p.nombre, "facultad": p.facultad} for p in profs],
            "asignaturas": [{"codigo": a.codigo, "nombre": a.nombre} for a in asigs],
            "facultades": sorted({p.facultad for p in profs} | {a.facultad for a in asigs}),
        }

    def crear_profesor(self, u: Usuario, d: ProfesorIn) -> dict:
        p = self.catalogo.guardar(Profesor(**d.model_dump()))
        self.auditoria.registrar(f"CREAR docente #{p.id} {p.nombre}", u.correo)
        return {"id": p.id, "nombre": p.nombre}

    def crear_asignatura(self, u: Usuario, d: AsignaturaIn) -> dict:
        codigo = d.codigo.upper()
        if self.catalogo.buscar_asignatura(codigo):
            raise AppError(409, "Ya existe una materia con ese código.", "codigo")
        a = self.catalogo.guardar(Asignatura(codigo=codigo, nombre=d.nombre, facultad=d.facultad, creditos=d.creditos))
        self.auditoria.registrar(f"CREAR asignatura {a.codigo}", u.correo)
        return {"codigo": a.codigo, "nombre": a.nombre}

    def crear_oferta(self, u: Usuario, d: OfertaIn) -> dict:
        codigo = d.asignatura_codigo.upper()
        if not self.catalogo.buscar_profesor(d.profesor_id):
            raise AppError(404, "El docente no existe.", "profesor_id")
        if not self.catalogo.buscar_asignatura(codigo):
            raise AppError(404, "La materia no existe. Créala primero.", "asignatura_codigo")
        try:
            o = self.catalogo.guardar(Oferta(profesor_id=d.profesor_id, asignatura_codigo=codigo,
                                             periodo=d.periodo, seccion=d.seccion.upper()))
        except ConflictoError:
            raise AppError(409, "Esa oferta ya existe (docente, materia, periodo y sección).", "seccion")
        self.auditoria.registrar(f"CREAR oferta #{o.id} ({codigo} {o.periodo} {o.seccion})", u.correo)
        return {"id": o.id}