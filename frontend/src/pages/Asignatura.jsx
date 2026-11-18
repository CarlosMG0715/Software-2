import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";

export default function Asignatura() {
  const { codigo } = useParams();
  const [d, setD] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api(`/asignaturas/${codigo}`).then(setD).catch((e) => setError(e.detail)); }, [codigo]);
  if (error) return <p role="alert">{error}</p>;
  if (!d) return <p>Cargando…</p>;
  return (
    <>
      <h1>{d.asignatura.codigo} · {d.asignatura.nombre}</h1>
      <p>{d.asignatura.facultad} · {d.asignatura.creditos} créditos</p>
      <ul className="lista">
        {d.docentes.map((x) => (
          <li key={x.profesor_id} className="tarjeta">
            <Link to={`/docentes/${x.profesor_id}`}><strong>{x.nombre}</strong></Link>
            {x.periodos.map((p) => (
              <span key={p.periodo}>{p.periodo}: {p.promedio != null ? `★ ${p.promedio}` : "sin reseñas"} ({p.total_resenas})</span>
            ))}
          </li>
        ))}
      </ul>
    </>
  );
}