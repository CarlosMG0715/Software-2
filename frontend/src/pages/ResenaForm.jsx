import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api.js";
import { Campo, errMap, EsqueletoPagina, focusCampo, Stars, useToast } from "../ui.jsx";

const TAGS = ["Exámenes largos", "Toma asistencia", "Talleres en grupo", "Sube la nota fácil", "Buen material"];
const CRITERIOS = [
  ["claridad", "Claridad", "1 = muy confusa · 3 = aceptable · 5 = muy clara"],
  ["exigencia", "Exigencia", "1 = muy poco exigente · 3 = moderada · 5 = muy exigente"],
  ["puntualidad", "Puntualidad", "1 = casi nunca puntual · 3 = a veces · 5 = siempre puntual"],
];
const VACIO = { oferta_id: "", claridad: 0, exigencia: 0, puntualidad: 0, recomienda: null, comentario: "", tags: [] };

export default function ResenaForm() {
  const { docenteId, id } = useParams();
  const edicion = !!id;
  const clave = `borrador:${edicion ? "edit" + id : docenteId}`;
  const nav = useNavigate();
  const toast = useToast();
  const [f, setF] = useState(() => (edicion ? VACIO : { ...VACIO, ...JSON.parse(localStorage.getItem(clave) || "{}") }));
  const [err, setErr] = useState({});
  const [ctx, setCtx] = useState(null); // { titulo, ofertas, bloqueadas }

  useEffect(() => {
    (async () => {
      try {
        const mias = await api("/resenas/mias");
        if (edicion) {
          const r = mias.find((x) => x.id === Number(id));
          if (!r) return nav("/panel");
          setCtx({ titulo: `${r.profesor_nombre} · ${r.asignatura_nombre} (${r.periodo})`, ofertas: [], bloqueadas: new Set() });
          const borrador = localStorage.getItem(clave);
          setF(borrador ? JSON.parse(borrador) : { ...VACIO, ...r, oferta_id: r.oferta_id });
        } else {
          const d = await api(`/docentes/${docenteId}`);
          const bloqueadas = new Set(mias.map((r) => `${r.profesor_id}|${r.asignatura_codigo}|${r.periodo}`));
          setCtx({ titulo: d.docente.nombre, ofertas: d.ofertas.map((o) => ({ ...o, bloqueada: bloqueadas.has(`${d.docente.id}|${o.asignatura_codigo}|${o.periodo}`) })) });
        }
      } catch (e) { toast(e.detail); }
    })();
  }, [id, docenteId]);

  useEffect(() => { localStorage.setItem(clave, JSON.stringify(f)); }, [f]); // borrador

  const set = (k, v) => setF((x) => ({ ...x, [k]: v }));
  const toggleTag = (t) => set("tags", f.tags.includes(t) ? f.tags.filter((x) => x !== t) : [...f.tags, t]);

  function validar() {
    const e = {};
    if (!edicion && !f.oferta_id) e.oferta_id = "Elige la materia y el periodo.";
    CRITERIOS.forEach(([k]) => { if (!f[k]) e[k] = "Selecciona una calificación."; });
    if (f.recomienda === null) e.recomienda = "Indica si recomiendas al docente.";
    const n = f.comentario.trim().length;
    if (n < 30 || n > 1000) e.comentario = "El comentario debe tener entre 30 y 1000 caracteres.";
    return e;
  }

  async function enviar(ev) {
    ev.preventDefault();
    let e = validar();
    if (!Object.keys(e).length) {
      const body = { claridad: f.claridad, exigencia: f.exigencia, puntualidad: f.puntualidad, recomienda: f.recomienda, comentario: f.comentario, tags: f.tags };
      try {
        if (edicion) await api(`/resenas/${id}`, { method: "PUT", body });
        else await api("/resenas", { method: "POST", body: { ...body, oferta_id: Number(f.oferta_id) } });
        localStorage.removeItem(clave);
        toast(edicion ? "Reseña enviada a moderación para revisión." : "Reseña enviada. Aparecerá cuando sea aprobada.");
        return nav("/panel");
      } catch (x) { e = errMap(x); if (!Object.keys(e).length) { toast(x.detail); return; } }
    }
    setErr(e);
    const primero = ["oferta_id", "claridad", "exigencia", "puntualidad", "recomienda", "comentario"].find((k) => e[k]);
    if (primero) setTimeout(() => focusCampo(primero), 0);
  }

  if (!ctx) return <EsqueletoPagina tipo="formulario" cantidad={3} />;
  return (
    <form onSubmit={enviar} className="tarjeta estrecha" noValidate>
      <h1>{edicion ? "Editar reseña" : "Nueva reseña"}</h1>
      <p><strong>{ctx.titulo}</strong></p>
      <p className="muted">Las reseñas se publican después de una revisión de moderación.</p>
      {!edicion && (
        <Campo nombre="oferta_id" etiqueta="Materia y periodo" error={err.oferta_id}>
          <select id="oferta_id" data-campo="oferta_id" value={f.oferta_id} onChange={(e) => set("oferta_id", e.target.value)}>
            <option value="">Selecciona…</option>
            {ctx.ofertas.map((o) => (
              <option key={o.id} value={o.id} disabled={o.bloqueada}>
                {o.asignatura_nombre} · {o.periodo} · sección {o.seccion}{o.bloqueada ? " (ya calificada)" : ""}
              </option>
            ))}
          </select>
        </Campo>
      )}
      {CRITERIOS.map(([k, nombre, escala]) => (
        <Campo key={k} nombre={k} etiqueta={nombre} ayuda={escala} error={err[k]}>
          <Stars nombre={k} etiqueta={nombre} valor={f[k]} onChange={(v) => set(k, v)} />
        </Campo>
      ))}
      <Campo nombre="recomienda" etiqueta="¿Recomiendas a este docente?" error={err.recomienda}>
        <div role="radiogroup" aria-label="Recomienda" data-campo="recomienda" className="fila">
          <button type="button" role="radio" aria-checked={f.recomienda === true} className={f.recomienda === true ? "sel" : ""} onClick={() => set("recomienda", true)}>Sí</button>
          <button type="button" role="radio" aria-checked={f.recomienda === false} className={f.recomienda === false ? "sel" : ""} onClick={() => set("recomienda", false)}>No</button>
        </div>
      </Campo>
      <Campo nombre="comentario" etiqueta="Comentario" error={err.comentario} ayuda="Entre 30 y 1000 caracteres. Sé respetuoso y concreto.">
        <textarea id="comentario" data-campo="comentario" rows={6} maxLength={1000} value={f.comentario} onChange={(e) => set("comentario", e.target.value)} />
        <small aria-live="polite">{f.comentario.trim().length}/1000 {f.comentario.trim().length < 30 && `(faltan ${30 - f.comentario.trim().length})`}</small>
      </Campo>
      <fieldset>
        <legend>Etiquetas (opcional)</legend>
        <div className="tags">
          {TAGS.map((t) => (
            <label key={t} className="check"><input type="checkbox" checked={f.tags.includes(t)} onChange={() => toggleTag(t)} />{t}</label>
          ))}
        </div>
      </fieldset>
      <button className="primario" type="submit">{edicion ? "Guardar cambios" : "Publicar reseña"}</button>
      <small>Tu borrador se guarda automáticamente en este dispositivo.</small>
    </form>
  );
}
