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