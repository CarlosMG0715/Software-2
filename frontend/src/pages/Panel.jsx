import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { useToast } from "../ui.jsx";
import { TarjetaResena } from "./Docente.jsx";

export default function Panel() {
  const [items, setItems] = useState(null);
  const toast = useToast();
  useEffect(() => { api("/resenas/mias").then(setItems).catch((e) => toast(e.detail)); }, []);

  function borrar(r) {
    let deshecho = false;
    setItems((x) => x.filter((i) => i.id !== r.id));
    toast("Reseña eliminada", {
      label: "Deshacer",
      fn: () => { deshecho = true; setItems((x) => [...x, r].sort((a, b) => b.id - a.id)); },
    }, 5000);
    setTimeout(async () => {
      if (deshecho) return;
      try { await api(`/resenas/${r.id}`, { method: "DELETE" }); }
      catch (e) { toast(e.detail); setItems((x) => [...x, r].sort((a, b) => b.id - a.id)); }
    }, 5200);
  }

  if (!items) return <p>Cargando…</p>;
  return (
    <>
      <h1>Mi panel</h1>
      {items.length === 0 ? <p>Aún no has escrito reseñas. <Link to="/">Busca un docente</Link>.</p> : (
        <ul className="lista">
          {items.map((r) => (
            <TarjetaResena key={r.id} r={r} acciones={
              <div className="fila">
                <span className={"estado " + r.estado}>{r.estado}</span>
                {!["rechazada", "eliminada"].includes(r.estado) && <Link className="boton" to={`/resena/editar/${r.id}`}>Editar</Link>}
                <button onClick={() => borrar(r)}>Eliminar</button>
              </div>
            } />
          ))}
        </ul>
      )}
    </>
  );
}