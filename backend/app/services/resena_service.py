from ..errors import AppError
from ..models import ESTADOS_PUBLICOS, EstadoResena, Reporte, Resena, Usuario, VotoUtilidad
from ..repositories.interfaces import ConflictoError, IProfesorRepository, IResenaRepository
from ..schemas import ResenaCrear, ResenaEditar
from ..security import hash_seudonimo
from .serializadores import resena_a_dict, serializar_lista


class ResenaService:
    def __init__(self, repo: IResenaRepository, profesores: IProfesorRepository):
        self.repo = repo
        self.profesores = profesores

    def _propia(self, usuario: Usuario, resena_id: int) -> Resena:
        r = self.repo.buscar_por_id(resena_id)
        if not r or r.autor_hash != hash_seudonimo(usuario.id):
            raise AppError(404, "La reseña no existe.")
        return r

    def _publica(self, resena_id: int) -> Resena:
        r = self.repo.buscar_por_id(resena_id)
        if not r or r.estado not in ESTADOS_PUBLICOS:
            raise AppError(404, "La reseña no existe.")
        return r

    def crear(self, usuario: Usuario, datos: ResenaCrear) -> dict:
        oferta = self.profesores.buscar_oferta(datos.oferta_id)
        if not oferta:
            raise AppError(404, "La oferta académica no existe.", "oferta_id")
        autor = hash_seudonimo(usuario.id)
        if self.repo.existe_para_autor(autor, oferta.profesor_id, oferta.asignatura_codigo, oferta.periodo):
            raise AppError(409, "Ya calificaste a este docente en esta materia y periodo.", "oferta_id")
        r = Resena(
            oferta_id=oferta.id, autor_hash=autor, claridad=datos.claridad, exigencia=datos.exigencia,
            puntualidad=datos.puntualidad, recomienda=datos.recomienda, comentario=datos.comentario,
            tags=datos.tags, estado=EstadoResena.PENDIENTE.value,
        )
        try:
            self.repo.guardar(r)
        except ConflictoError:
            raise AppError(409, "Ya calificaste a este docente en esta materia y periodo.", "oferta_id")
        return resena_a_dict(r, incluir_estado=True)

    def editar(self, usuario: Usuario, resena_id: int, datos: ResenaEditar) -> dict:
        r = self._propia(usuario, resena_id)
        if r.estado in (EstadoResena.RECHAZADA.value, EstadoResena.ELIMINADA.value):
            raise AppError(403, "Esta reseña ya no se puede editar.")
        r.claridad, r.exigencia, r.puntualidad = datos.claridad, datos.exigencia, datos.puntualidad
        r.recomienda, r.comentario, r.tags = datos.recomienda, datos.comentario, datos.tags
        r.estado = EstadoResena.PENDIENTE.value
        self.repo.guardar(r)
        return resena_a_dict(r, incluir_estado=True)

    def eliminar(self, usuario: Usuario, resena_id: int) -> None:
        self.repo.eliminar(self._propia(usuario, resena_id))

    def mias(self, usuario: Usuario) -> list[dict]:
        return serializar_lista(self.repo, self.repo.buscar_por_autor(hash_seudonimo(usuario.id)), incluir_estado=True)

    def votar(self, usuario: Usuario, resena_id: int, es_util: bool) -> dict:
        r = self._publica(resena_id)
        uh = hash_seudonimo(usuario.id)
        if self.repo.existe_voto(r.id, uh):
            raise AppError(409, "Ya votaste esta reseña.")
        try:
            self.repo.agregar_voto(VotoUtilidad(resena_id=r.id, usuario_hash=uh, es_util=es_util))
        except ConflictoError:
            raise AppError(409, "Ya votaste esta reseña.")
        utiles, no_utiles = self.repo.votos_resumen([r.id]).get(r.id, (0, 0))
        return {"utiles": utiles, "no_utiles": no_utiles}

    def reportar(self, usuario: Usuario, resena_id: int, motivo: str) -> dict:
        r = self._publica(resena_id)
        rh = hash_seudonimo(usuario.id)
        if self.repo.existe_reporte(r.id, rh):
            raise AppError(409, "Ya reportaste esta reseña.")
        try:
            self.repo.agregar_reporte(Reporte(resena_id=r.id, reportante_hash=rh, motivo=motivo))
        except ConflictoError:
            raise AppError(409, "Ya reportaste esta reseña.")
        self.repo.guardar(r)
        return {"mensaje": "Reporte enviado. Gracias por ayudar a moderar."}
