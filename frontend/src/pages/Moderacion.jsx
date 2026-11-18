import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useToast } from "../ui.jsx";
import { TarjetaResena } from "./Docente.jsx";

export default function Moderacion() {
  const [items, setItems] = useState(null);
  const [audit, setAudit] = useState([]);
  const toast = useToast();

  const cargar = () => {
    api("/moderacion/reportadas").then(setItems).catch((e) => toast(e.detail));
    api("/moderacion/auditoria").then(setAudit).catch(() => {});
  };
  useEffect(cargar, []);

  async function accion(r, tipo) {
    if (tipo === "eliminar" && !window.confirm("¿Eliminar definitivamente esta reseña del público?")) return;
    try { await api(`/moderacion/${r.id}/${tipo}`, { method: "POST" }); toast("Acción aplicada"); cargar(); }
    catch (e) { toast(e.detail); }
  }

  if (!items) return <p>Cargando…</p>;
  return (
    <>
      <h1>Moderación</h1>
      <h2>Reseñas reportadas</h2>
      {items.length === 0 ? <p>No hay reseñas reportadas.</p> : (
        <ul className="lista">
          {items.map((r) => (
            <TarjetaResena key={r.id} r={r} acciones={
              <>
                <p><span className={"estado " + r.estado}>{r.estado}</span> · {r.num_reportes} reportes: {r.motivos.join(" | ")}</p>
                <div className="fila">
                  <button onClick={() => accion(r, "aprobar")}>Aprobar</button>
                  <button onClick={() => accion(r, "rechazar")}>Rechazar</button>
                  <button className="peligro" onClick={() => accion(r, "eliminar")}>Eliminar</button>
                </div>
              </>
            } />
          ))}
        </ul>
      )}
      <h2>Auditoría</h2>
      <div className="scroll">
        <table>
          <thead><tr><th>Fecha</th><th>Acción</th><th>Ejecutado por</th></tr></thead>
          <tbody>
            {audit.map((a) => (
              <tr key={a.id}><td>{new Date(a.fecha).toLocaleString("es-CO")}</td><td>{a.accion}</td><td>{a.ejecutado_por}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}