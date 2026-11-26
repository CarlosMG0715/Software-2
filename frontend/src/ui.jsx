import { createContext, useCallback, useContext, useRef, useState } from "react";

const T = createContext(() => {});
export const useToast = () => useContext(T);

export function ToastProvider({ children }) {
  const [items, setItems] = useState([]);
  const id = useRef(0);
  const quitar = (i) => setItems((x) => x.filter((t) => t.id !== i));
  const push = useCallback((msg, accion, ms = 4000) => {
    const i = ++id.current;
    setItems((x) => [...x, { id: i, msg, accion }]);
    setTimeout(() => quitar(i), ms);
  }, []);
  return (
    <T.Provider value={push}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {items.map((t) => (
          <div key={t.id} className="toast">
            <span>{t.msg}</span>
            {t.accion && (
              <button onClick={() => { t.accion.fn(); quitar(t.id); }}>{t.accion.label}</button>
            )}
          </div>
        ))}
      </div>
    </T.Provider>
  );
}

export const errMap = (e) => Object.fromEntries((e.errores || []).filter((x) => x.campo).map((x) => [x.campo, x.mensaje]));

export function focusCampo(campo) {
  const el = document.querySelector(`[data-campo="${campo}"]`);
  if (!el) return;
  (el.matches("button,input,select,textarea") ? el : el.querySelector("button,input,select,textarea"))?.focus();
}

export function Campo({ nombre, etiqueta, error, ayuda, children }) {
  return (
    <div className={"campo" + (error ? " error" : "")}>
      <label htmlFor={nombre}>{etiqueta}</label>
      {ayuda && <small>{ayuda}</small>}
      {children}
      {error && <span className="msg" role="alert">{error}</span>}
    </div>
  );
}

// Skeletons preserve each page's rough layout while its data request is pending.
export function EsqueletoPagina({ tipo = "lista", cantidad = 3 }) {
  return (
    <section className={`esqueleto-pagina esqueleto-pagina--${tipo}`} role="status" aria-label="Cargando contenido" aria-busy="true">
      <span className="solo-lectores">Cargando contenido…</span>
      <div className="esqueleto-pagina__cuerpo" aria-hidden="true">
        {tipo !== "directorio" && <><span className="esqueleto-barra esqueleto-barra--titulo" /><span className="esqueleto-barra esqueleto-barra--subtitulo" /></>}
        {tipo === "detalle" && <><div className="esqueleto-tarjeta esqueleto-tarjeta--resumen"><span className="esqueleto-barra esqueleto-barra--media" /><span className="esqueleto-barra" /></div><span className="esqueleto-barra esqueleto-barra--seccion" /></>}
        {tipo === "metricas" && <div className="esqueleto-metricas"><span className="esqueleto-tarjeta" /><span className="esqueleto-tarjeta" /><span className="esqueleto-tarjeta" /></div>}
        {tipo === "formulario" ? <div className="esqueleto-formulario">{Array.from({ length: 6 }, (_, i) => <span key={i} className="esqueleto-campo"><i /><b /></span>)}</div> : (
          <div className="esqueleto-lista">{Array.from({ length: cantidad }, (_, i) => <div className="esqueleto-tarjeta" key={i}><span className="esqueleto-barra esqueleto-barra--media" /><span className="esqueleto-barra" /><span className="esqueleto-barra esqueleto-barra--corta" /></div>)}</div>
        )}
      </div>
    </section>
  );
}

export function Stars({ valor, onChange, nombre, etiqueta }) {
  const set = (n) => onChange(Math.min(5, Math.max(1, n)));
  const tecla = (e) => {
    if (["ArrowRight", "ArrowUp"].includes(e.key)) { e.preventDefault(); set((valor || 0) + 1); }
    if (["ArrowLeft", "ArrowDown"].includes(e.key)) { e.preventDefault(); set((valor || 2) - 1); }
  };
  return (
    <div role="radiogroup" aria-label={etiqueta} data-campo={nombre} className="stars" onKeyDown={tecla}>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          type="button" key={n} role="radio" aria-checked={valor === n}
          aria-label={`${n} de 5`} tabIndex={valor === n || (!valor && n === 1) ? 0 : -1}
          className={n <= valor ? "on" : ""} onClick={() => set(n)}
        >★</button>
      ))}
    </div>
  );
}

export const Promedio = ({ v }) => (v == null ? "Sin reseñas" : `★ ${Number(v).toFixed(1)}`);
