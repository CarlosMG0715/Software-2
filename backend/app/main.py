from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .errors import registrar_manejadores
from .routers import asignaturas, auth, docentes, metricas, moderacion, resenas

app = FastAPI(title="Evaluación Docente Anónima", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
registrar_manejadores(app)

for r in (auth.router, docentes.router, asignaturas.router, resenas.router, moderacion.router, metricas.router):
    app.include_router(r, prefix="/api")