from fastapi import APIRouter, Depends, Response

from ..deps import get_resena_service, requiere_roles
from ..models import Rol, Usuario
from ..schemas import ReporteIn, ResenaCrear, ResenaEditar, VotoIn
from ..services.resena_service import ResenaService

router = APIRouter(prefix="/resenas", tags=["reseñas"])
estudiante = requiere_roles(Rol.ESTUDIANTE)


@router.post("", status_code=201)
def crear(datos: ResenaCrear, u: Usuario = Depends(estudiante), s: ResenaService = Depends(get_resena_service)):
    return s.crear(u, datos)


@router.get("/mias")
def mias(u: Usuario = Depends(estudiante), s: ResenaService = Depends(get_resena_service)):
    return s.mias(u)


@router.put("/{resena_id}")
def editar(resena_id: int, datos: ResenaEditar, u: Usuario = Depends(estudiante),
           s: ResenaService = Depends(get_resena_service)):
    return s.editar(u, resena_id, datos)


@router.delete("/{resena_id}", status_code=204)
def eliminar(resena_id: int, u: Usuario = Depends(estudiante), s: ResenaService = Depends(get_resena_service)):
    s.eliminar(u, resena_id)
    return Response(status_code=204)


@router.post("/{resena_id}/voto")
def votar(resena_id: int, datos: VotoIn, u: Usuario = Depends(estudiante),
          s: ResenaService = Depends(get_resena_service)):
    return s.votar(u, resena_id, datos.es_util)


@router.post("/{resena_id}/reporte", status_code=201)
def reportar(resena_id: int, datos: ReporteIn, u: Usuario = Depends(estudiante),
             s: ResenaService = Depends(get_resena_service)):
    return s.reportar(u, resena_id, datos.motivo)