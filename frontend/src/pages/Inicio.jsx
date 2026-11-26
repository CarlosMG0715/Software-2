import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { Promedio, useToast } from "../ui.jsx";
import { useAuth } from "../auth.jsx";

export default function Inicio() {
  const [p, setP] = useState({ q: "", tipo: "profesor", facultad: "", promedio_min: "", orden: "promedio_desc" });
  const [items, setItems] = useState(null);
  const [facs, setFacs] = useState([]);
  const toast = useToast();
  const { user } = useAuth();
  const set = (k) => (e) => setP({ ...p, [k]: e.target.value });

  useEffect(() => {
    api("/docentes?orden=nombre").then((l) => setFacs([...new Set(l.map((d) => d.facultad))])).catch(() => {});
  }, []);

  useEffect(() => {
    let vivo = true;
    const qs = new URLSearchParams(Object.entries(p).filter(([, v]) => v !== "")).toString();
    api("/docentes?" + qs).then((l) => vivo && setItems(l)).catch((e) => toast(e.detail));
    return () => { vivo = false; };
  }, [p]);

  return (
    <>
    {!user && <section className="portada">
      <div className="portada__contenido">
        <span className="portada__etiqueta">COMUNIDAD ACADÉMICA</span>
        <h1>Elige tus clases con más información.</h1>
        <p>Consulta experiencias reales de estudiantes y comparte tu opinión sobre docentes y asignaturas de forma responsable.</p>
        <div className="portada__acciones">
          <Link className="boton primario" to="/login?modo=registro">Crear una cuenta</Link>
          <Link className="boton portada__secundario" to="/login">Ingresar</Link>
        </div>
        <div className="portada__puntos"><span>Reseñas de estudiantes</span><span>Información para decidir</span><span>Comunidad universitaria</span></div>
      </div>
      <div className="portada__visual" aria-hidden="true">
        <div className="portada__tarjeta"><span className="portada__estrella">★ ★ ★ ★ ★</span><strong>Una mejor decisión empieza con información.</strong><small>Experiencias compartidas por estudiantes</small></div>
        <span className="portada__orbita">✳</span>
      </div>
    </section>}
    <section className="explorar" id="profesores">
      <div className="explorar__titulo">
        <div><span className="portada__etiqueta">DIRECTORIO ACADÉMICO</span>{user ? <h1>Profesores</h1> : <h2>Profesores</h2>}</div>
      </div>
      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <input aria-label="Buscar" placeholder="Buscar profesor…" value={p.q} onChange={set("q")} />
        <select aria-label="Buscar por" value={p.tipo} onChange={set("tipo")}>
          <option value="profesor">Por profesor</option>
          <option value="codigo">Por código</option>
          <option value="materia">Por materia</option>
        </select>
        <select aria-label="Facultad" value={p.facultad} onChange={set("facultad")}>
          <option value="">Todas las facultades</option>
          {facs.map((f) => <option key={f}>{f}</option>)}
        </select>
        <select aria-label="Promedio mínimo" value={p.promedio_min} onChange={set("promedio_min")}>
          <option value="">Cualquier promedio</option>
          {[3, 3.5, 4, 4.5].map((n) => <option key={n} value={n}>≥ {n}</option>)}
        </select>
        <select aria-label="Ordenar" value={p.orden} onChange={set("orden")}>
          <option value="promedio_desc">Mejor promedio</option>
          <option value="promedio_asc">Menor promedio</option>
          <option value="resenas">Más reseñas</option>
          <option value="nombre">Nombre</option>
        </select>
      </form>
      {!items ? <p>Cargando…</p> : items.length === 0 ? <p>Sin resultados.</p> : (
        <ul className="lista directorio-lista">
          {items.map((d) => (
            <li key={d.id} className="tarjeta directorio-card">
              <Link to={`/docentes/${d.id}`} aria-label={user ? `Ver reseñas de ${d.nombre}` : "Ver hasta dos reseñas de un profesor"}>
                <strong className={user ? "" : "nombre-reservado"}>{d.nombre}</strong>
              </Link>
              <span>{d.departamento} · {d.facultad}</span>
              <span><Promedio v={d.promedio} /> · {d.total_resenas} reseñas</span>
              <Link className="directorio-card__accion" to={`/docentes/${d.id}`}>Ver reseñas</Link>
            </li>
          ))}
        </ul>
      )}
      {!user && items && (
        <aside className="registro-prompt">
          <strong>¿Quieres conocer más?</strong>
          <p>Regístrate para ver más reseñas y nombres de profesores.</p>
          <Link className="boton primario" to="/login?modo=registro">Registrarme</Link>
        </aside>
      )}
    </section>
    </>
  );
}
