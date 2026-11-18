import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Campo, errMap, focusCampo, useToast } from "../ui.jsx";

function Formulario({ titulo, ruta, campos, onOk }) {
  const vacio = Object.fromEntries(campos.map((c) => [c.k, ""]));
  const [f, setF] = useState(vacio);
  const [err, setErr] = useState({});
  const toast = useToast();

  async function enviar(ev) {
    ev.preventDefault();
    setErr({});
    const body = Object.fromEntries(
      campos.map((c) => [c.k, c.tipo === "number" || c.num ? (f[c.k] === "" ? null : Number(f[c.k])) : f[c.k]])
    );
    try {
      await api(ruta, { method: "POST", body });
      toast(titulo + ": creado");
      setF(vacio);
      onOk();
    } catch (e) {
      const m = errMap(e);
      if (!Object.keys(m).length) return toast(e.detail);
      setErr(m);
      const primero = campos.find((c) => m[c.k]);
      if (primero) setTimeout(() => focusCampo(primero.k), 0);
    }
  }

  return (
    <form onSubmit={enviar} className="tarjeta" noValidate>
      <h2>{titulo}</h2>
      {campos.map((c) => (
        <Campo key={c.k} nombre={c.k} etiqueta={c.label} ayuda={c.ayuda} error={err[c.k]}>
          {c.opciones ? (
            <select id={c.k} data-campo={c.k} value={f[c.k]} onChange={(e) => setF({ ...f, [c.k]: e.target.value })}>
              <option value="">Selecciona…</option>
              {c.opciones.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
            </select>
          ) : (
            <input id={c.k} data-campo={c.k} type={c.tipo || "text"} list={c.lista} value={f[c.k]}
              onChange={(e) => setF({ ...f, [c.k]: e.target.value })} />
          )}
        </Campo>
      ))}
      <button className="primario" type="submit">Crear</button>
    </form>
  );
}

export default function Admin() {
  const [cat, setCat] = useState(null);
  const toast = useToast();
  const cargar = () => api("/admin/catalogo").then(setCat).catch((e) => toast(e.detail));
  useEffect(() => { cargar(); }, []);
  if (!cat) return <p>Cargando…</p>;

  return (
    <>
      <h1>Administración</h1>
      <datalist id="facultades">{cat.facultades.map((x) => <option key={x} value={x} />)}</datalist>
      <Formulario titulo="Nuevo docente" ruta="/admin/profesores" onOk={cargar} campos={[
        { k: "nombre", label: "Nombre completo" },
        { k: "departamento", label: "Departamento" },
        { k: "facultad", label: "Facultad", lista: "facultades", ayuda: "Elige una existente para no duplicarla." },
      ]} />
      <Formulario titulo="Nueva materia" ruta="/admin/asignaturas" onOk={cargar} campos={[
        { k: "codigo", label: "Código", ayuda: "Ej.: QUI101" },
        { k: "nombre", label: "Nombre" },
        { k: "facultad", label: "Facultad", lista: "facultades" },
        { k: "creditos", label: "Créditos", tipo: "number" },
      ]} />
      <Formulario titulo="Nueva oferta (docente + materia + periodo)" ruta="/admin/ofertas" onOk={cargar} campos={[
        { k: "profesor_id", label: "Docente", num: true, opciones: cat.profesores.map((p) => [p.id, p.nombre]) },
        { k: "asignatura_codigo", label: "Materia", opciones: cat.asignaturas.map((a) => [a.codigo, `${a.codigo} · ${a.nombre}`]) },
        { k: "periodo", label: "Periodo", ayuda: "Formato 2026-1" },
        { k: "seccion", label: "Sección", ayuda: "Ej.: A" },
      ]} />
    </>
  );
}