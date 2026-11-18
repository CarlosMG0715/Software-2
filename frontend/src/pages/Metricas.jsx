import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useToast } from "../ui.jsx";

export default function Metricas() {
  const [m, setM] = useState(null);
  const toast = useToast();
  useEffect(() => { api("/metricas/docente").then(setM).catch((e) => toast(e.detail)); }, []);

  async function pdf() {
    try {
      const b = await api("/metricas/docente/pdf", { blob: true });
      const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(b), download: "metricas-docente.pdf" });
      a.click();
      URL.revokeObjectURL(a.href);
      toast("PDF descargado");
    } catch (e) { toast(e.detail); }
  }

  if (!m) return <p>Cargando…</p>;
  const max = Math.max(1, ...Object.values(m.tags));
  return (
    <>
      <h1>Mis métricas</h1>
      <p>{m.docente.nombre} · {m.docente.departamento}</p>
      <div className="tarjeta">
        <strong>★ {m.promedio}</strong> promedio · {m.total} reseñas · {m.pct_recomienda}% recomienda
        <br />Claridad {m.promedios.claridad} · Exigencia {m.promedios.exigencia} · Puntualidad {m.promedios.puntualidad}
      </div>
      <h2>Etiquetas</h2>
      <div role="img" aria-label="Gráfico de barras de etiquetas">
        {Object.entries(m.tags).map(([t, c]) => (
          <div key={t} className="barra">
            <span>{t}</span>
            <div><i style={{ width: `${(c / max) * 100}%` }} /></div>
            <b>{c}</b>
          </div>
        ))}
      </div>
      <button className="primario" onClick={pdf}>Descargar PDF</button>
    </>
  );
}