import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { EsqueletoPagina, useToast } from "../ui.jsx";

export const TarjetaResena = ({ r, acciones }) => (
  <li className="tarjeta">
    <div><strong>{r.asignatura_nombre}</strong> · {r.periodo} · {r.recomienda ? "👍 Recomienda" : "👎 No recomienda"}</div>
    <div>Claridad {r.claridad} · Exigencia {r.exigencia} · Puntualidad {r.puntualidad}</div>
    <p>{r.comentario}</p>
    {r.tags.length > 0 && <div className="tags">{r.tags.map((t) => <span key={t}>{t}</span>)}</div>}
    <small>{new Date(r.creada).toLocaleDateString("es-CO")} · {r.utiles} útil · {r.no_utiles} no útil</small>
    {acciones}
  </li>
);

export default function Docente() {
  const { id } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const [d, setD] = useState(null);
  const [error, setError] = useState("");

  const cargar = () => api(`/docentes/${id}`).then(setD).catch((e) => setError(e.detail));
  useEffect(() => { cargar(); }, [id]);

  async function votar(r, es_util) {
    try { await api(`/resenas/${r.id}/voto`, { method: "POST", body: { es_util } }); toast("Voto registrado"); cargar(); }
    catch (e) { toast(e.detail); }
  }
  async function reportar(r) {
    const motivo = window.prompt("¿Por qué reportas esta reseña? (mín. 3 caracteres)");
    if (!motivo) return;
    try { const x = await api(`/resenas/${r.id}/reporte`, { method: "POST", body: { motivo } }); toast(x.mensaje); }
    catch (e) { toast(e.detail); }
  }

  if (error) return <p role="alert">{error}</p>;
  if (!d) return <EsqueletoPagina tipo="detalle" cantidad={3} />;
  const est = user?.rol === "ESTUDIANTE";
  const { promedios: p } = d;
  const resenasVisibles = user ? d.resenas : d.resenas.slice(0, 2);
  return (
    <>
      <h1 className={user ? "" : "nombre-reservado"} aria-label={user ? undefined : "Nombre reservado; regístrate para verlo"}>{d.docente.nombre}</h1>
      <p>{d.docente.departamento} · {d.docente.facultad}</p>
      <div className="tarjeta">
        <strong>★ {p.general}</strong> general · Claridad {p.claridad} · Exigencia {p.exigencia} · Puntualidad {p.puntualidad}
        <br />{d.pct_recomienda}% recomienda · {d.total_resenas} reseñas
      </div>
      {est && <Link className="boton primario" to={`/resena/nueva/${id}`}>Calificar a este docente</Link>}
      <h2>Materias</h2>
      <ul className="inline">
        {[...new Map(d.ofertas.map((o) => [o.asignatura_codigo, o])).values()].map((o) => (
          <li key={o.asignatura_codigo}><Link to={`/asignaturas/${o.asignatura_codigo}`}>{o.asignatura_codigo} · {o.asignatura_nombre}</Link></li>
        ))}
      </ul>
      <h2>Reseñas</h2>
      {resenasVisibles.length === 0 ? <p>Aún no hay reseñas.</p> : (
        <ul className="lista">
          {resenasVisibles.map((r) => (
            <TarjetaResena key={r.id} r={r} acciones={est && (
              <div className="fila">
                <button onClick={() => votar(r, true)}>👍 Útil</button>
                <button onClick={() => votar(r, false)}>👎 No útil</button>
                <button onClick={() => reportar(r)}>🚩 Reportar</button>
              </div>
            )} />
          ))}
        </ul>
      )}
      {!user && <aside className="registro-prompt">
        <strong>¿Quieres ver más?</strong>
        <p>Regístrate para ver más reseñas y nombres de profesores.</p>
        <Link className="boton primario" to="/login?modo=registro">Crear cuenta</Link>
      </aside>}
    </>
  );
}
