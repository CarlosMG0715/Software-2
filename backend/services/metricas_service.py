from collections import Counter
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..errors import AppError
from ..models import TAGS_PREDEFINIDOS, Resena, Usuario
from ..repositories.interfaces import IProfesorRepository, IResenaRepository

CRITERIOS = ("claridad", "exigencia", "puntualidad")


def calcular_metricas(resenas: list[Resena]) -> dict:
    n = len(resenas)
    prom = {c: (round(sum(getattr(r, c) for r in resenas) / n, 2) if n else 0) for c in CRITERIOS}
    general = round(sum(prom.values()) / 3, 2) if n else 0
    pct = round(100 * sum(1 for r in resenas if r.recomienda) / n, 1) if n else 0
    cont = Counter(t for r in resenas for t in (r.tags or []))
    return {
        "promedios": {**prom, "general": general},
        "total": n,
        "pct_recomienda": pct,
        "tags": {t: cont.get(t, 0) for t in TAGS_PREDEFINIDOS},
    }


class MetricasService:
    def __init__(self, profesores: IProfesorRepository, resenas: IResenaRepository):
        self.profesores = profesores
        self.resenas = resenas

    def _profesor(self, usuario: Usuario):
        p = self.profesores.buscar_por_id(usuario.profesor_id) if usuario.profesor_id else None
        if not p:
            raise AppError(404, "Tu usuario no está vinculado a un docente.")
        return p

    def docente(self, usuario: Usuario) -> dict:
        p = self._profesor(usuario)
        m = calcular_metricas(self.resenas.buscar_por_profesor(p.id))
        return {"docente": {"id": p.id, "nombre": p.nombre, "departamento": p.departamento, "facultad": p.facultad},
                "promedio": m["promedios"]["general"], **m}

    def pdf(self, usuario: Usuario) -> bytes:
        d = self.docente(usuario)
        est = getSampleStyleSheet()
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, title="Métricas docente")
        filas = [
            ["Indicador", "Valor"],
            ["Promedio general", d["promedio"]],
            ["Claridad", d["promedios"]["claridad"]],
            ["Exigencia", d["promedios"]["exigencia"]],
            ["Puntualidad", d["promedios"]["puntualidad"]],
            ["Total de reseñas", d["total"]],
            ["% que recomienda", f'{d["pct_recomienda"]}%'],
        ]
        filas_tags = [["Etiqueta", "Conteo"]] + [[t, c] for t, c in d["tags"].items()]
        estilo = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        t1, t2 = Table(filas, colWidths=[260, 120]), Table(filas_tags, colWidths=[260, 120])
        t1.setStyle(estilo)
        t2.setStyle(estilo)
        doc.build([
            Paragraph(f'Métricas - {d["docente"]["nombre"]}', est["Title"]),
            Paragraph(f'{d["docente"]["departamento"]} · {d["docente"]["facultad"]}', est["Normal"]),
            Paragraph(f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}', est["Normal"]),
            Spacer(1, 16), t1, Spacer(1, 16), Paragraph("Etiquetas", est["Heading2"]), t2,
        ])
        return buf.getvalue()