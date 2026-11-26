from ..errors import AppError
from ..models import EstadoResena, Usuario
from ..repositories.interfaces import IResenaRepository
from ..repositories.sql import SqlAuditRepository
from .serializadores import resena_a_dict


class ModeracionService:
    """Gestiona aprobaciones previas y reportes enviados por la comunidad."""

    def __init__(self, resenas: IResenaRepository, auditoria: SqlAuditRepository):
        self.resenas = resenas
        self.auditoria = auditoria

    def cola(self) -> list[dict]:
        lista = self.resenas.cola_moderacion()
        motivos = self.resenas.reportes_de([r.id for r in lista])
        resumen = self.resenas.votos_resumen([r.id for r in lista])
        items = [
            {**resena_a_dict(r, resumen.get(r.id, (0, 0)), incluir_estado=True),
             "num_reportes": len(motivos[r.id]), "motivos": motivos[r.id]}
            for r in lista
        ]
        items.sort(key=lambda i: -i["num_reportes"])
        return items

    def _accion(self, usuario: Usuario, resena_id: int, nuevo: EstadoResena, etiqueta: str) -> dict:
        r = self.resenas.buscar_por_id(resena_id)
        if not r or r.estado == EstadoResena.ELIMINADA.value:
            raise AppError(404, "La reseña no existe.")
        if nuevo == EstadoResena.APROBADA:
            self.resenas.limpiar_reportes(r.id)  # aprobar reinicia los reportes
        r.estado = nuevo.value
        self.auditoria.registrar(f"{etiqueta} resena #{r.id}", usuario.correo, commit=False)
        self.resenas.guardar(r)  # un solo commit: cambio + auditoría
        return {"id": r.id, "estado": r.estado}

    def aprobar(self, usuario: Usuario, resena_id: int) -> dict:
        return self._accion(usuario, resena_id, EstadoResena.APROBADA, "APROBAR")

    def rechazar(self, usuario: Usuario, resena_id: int) -> dict:
        return self._accion(usuario, resena_id, EstadoResena.RECHAZADA, "RECHAZAR")

    def eliminar(self, usuario: Usuario, resena_id: int) -> dict:
        return self._accion(usuario, resena_id, EstadoResena.ELIMINADA, "ELIMINAR")

    def auditoria_lista(self) -> list[dict]:
        return [{"id": a.id, "fecha": a.fecha, "accion": a.accion, "ejecutado_por": a.ejecutado_por}
                for a in self.auditoria.listar()]
