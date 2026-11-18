import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { Promedio, useToast } from "../ui.jsx";

export default function Inicio() {
  const [p, setP] = useState({ q: "", tipo: "profesor", facultad: "", promedio_min: "", orden: "promedio_desc" });
  const [items, setItems] = useState(null);
  const [facs, setFacs] = useState([]);
  const toast = useToast();
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
      <h1>Evalúa a tus docentes</h1>
      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <input aria-label="Buscar" placeholder="Buscar…" value={p.q} onChange={set("q")} />
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
        <ul className="lista">
          {items.map((d) => (
            <li key={d.id} className="tarjeta">
              <Link to={`/docentes/${d.id}`}><strong>{d.nombre}</strong></Link>
              <span>{d.departamento} · {d.facultad}</span>
              <span><Promedio v={d.promedio} /> · {d.total_resenas} reseñas{d.pct_recomienda != null && ` · ${d.pct_recomienda}% recomienda`}</span>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}