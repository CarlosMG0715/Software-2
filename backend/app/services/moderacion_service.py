from ..errors import AppError
from ..models import ESTADOS_PUBLICOS, EstadoResena, Resena, Usuario
from ..repositories.interfaces import IResenaRepository
from ..repositories.sql import SqlAuditRepository
from .serializadores import resena_a_dict

UMBRAL_REPORTES = 5


class ModeracionService:
    """Observer de Resena: oculta la reseña al alcanzar 5 reportes de usuarios distintos."""

    def __init__(self, resenas: IResenaRepository, auditoria: SqlAuditRepository):
        self.resenas = resenas
        self.auditoria = auditoria

    # --- Observer ---
    def actualizar(self, resena: Resena) -> None:
        if resena.estado not in ESTADOS_PUBLICOS:
            return
        # (resena_id, reportante_hash) es PK: cada reporte es de un usuario distinto.
        if self.resenas.contar_reportes(resena.id) >= UMBRAL_REPORTES:
            resena.estado = EstadoResena.OCULTA.value
            self.auditoria.registrar(f"OCULTAR_AUTOMATICO resena #{resena.id} ({UMBRAL_REPORTES} reportes)", "sistema", commit=False)

    # --- Casos de uso de moderación ---
    def reportadas(self) -> list[dict]:
        lista = self.resenas.reportadas()
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