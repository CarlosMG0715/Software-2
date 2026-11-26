import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { Campo, errMap, focusCampo, useToast } from "../ui.jsx";

export default function Login() {
  const [params] = useSearchParams();
  // Supports direct entry from the home page's create account button.
  const [modo, setModo] = useState(params.get("modo") === "registro" ? "registro" : "login");
  const [f, setF] = useState({ nombre: "", correo: "", password: "", repetir: "", acepta: false });
  const [err, setErr] = useState({});
  const { login } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });
  const reglasClave = [f.password.length >= 8, /[a-z]/.test(f.password) && /[A-Z]/.test(f.password), /\d/.test(f.password), /[^A-Za-z0-9]/.test(f.password)];
  const nivelClave = reglasClave.filter(Boolean).length;
  const nivelTexto = ["Muy débil", "Débil", "Aceptable", "Buena", "Fuerte"][nivelClave];

  const fallo = (e) => {
    const m = errMap(e);
    if (!Object.keys(m).length) m.general = e.detail;
    setErr(m);
    const primero = Object.keys(m).find((k) => k !== "general");
    if (primero) setTimeout(() => focusCampo(primero), 0);
  };

  async function enviar(ev) {
    ev.preventDefault();
    setErr({});
    try {
      if (modo === "login") {
        login(await api("/auth/login", { method: "POST", body: { correo: f.correo, password: f.password } }));
        toast("Bienvenido/a");
        nav("/");
        return;
      }

      if (f.password !== f.repetir) {
        setErr({ repetir: "Las contraseñas no coinciden." });
        setTimeout(() => focusCampo("repetir"), 0);
        return;
      }

      const r = await api("/auth/registrar", {
        method: "POST",
        body: { nombre: f.nombre, correo: f.correo, password: f.password, acepta_ley_1581: f.acepta },
      });
      login(r);
      toast(r.mensaje);
      nav("/panel");
    } catch (e) { fallo(e); }
  }

  const registro = modo === "registro";
  return (
    <div className="login-pagina">
    <form onSubmit={enviar} className="tarjeta estrecha" noValidate>
      <h1>{registro ? "Crear cuenta" : "Ingresar"}</h1>
      {err.general && <p className="msg" role="alert">{err.general}</p>}
      {registro && (
        <Campo nombre="nombre" etiqueta="Nombre de usuario" error={err.nombre}>
          <input id="nombre" data-campo="nombre" value={f.nombre} onChange={set("nombre")} autoComplete="username" placeholder="Elige tu nombre de usuario" required />
        </Campo>
      )}
      <Campo nombre="correo" etiqueta="Correo institucional" error={err.correo}>
        <input id="correo" data-campo="correo" type="email" value={f.correo} onChange={set("correo")} autoComplete="email" required />
      </Campo>
      <Campo nombre="password" etiqueta="Contraseña" error={err.password} ayuda={registro ? "Mínimo 8 caracteres." : null}>
        <input id="password" data-campo="password" type="password" value={f.password} onChange={set("password")} autoComplete={registro ? "new-password" : "current-password"} required />
      </Campo>
      {registro && f.password && (
        <div className="fuerza-clave" aria-live="polite">
          <div className="fuerza-clave__encabezado"><span>Seguridad de la contraseña</span><strong>{nivelTexto}</strong></div>
          <div className="fuerza-clave__barra" role="meter" aria-label="Seguridad de la contraseña" aria-valuemin="0" aria-valuemax="4" aria-valuenow={nivelClave}>
            {reglasClave.map((cumple, i) => <span key={i} className={cumple ? "cumple" : ""} />)}
          </div>
          <ul className="fuerza-clave__reglas">
            {["8 caracteres", "Mayúsculas y minúsculas", "Un número", "Un símbolo"].map((regla, i) => <li key={regla} className={reglasClave[i] ? "cumple" : ""}>{regla}</li>)}
          </ul>
        </div>
      )}
      {registro && (
        <>
          <Campo nombre="repetir" etiqueta="Repetir contraseña" error={err.repetir}>
            <input id="repetir" data-campo="repetir" type="password" value={f.repetir} onChange={set("repetir")} autoComplete="new-password" required />
          </Campo>
          <Campo nombre="acepta_ley_1581" error={err.acepta_ley_1581} etiqueta="">
            <label className="check">
              <input id="acepta_ley_1581" data-campo="acepta_ley_1581" type="checkbox" checked={f.acepta} onChange={set("acepta")} />
              Autorizo el tratamiento de mis datos personales (Ley 1581 de 2012).
            </label>
          </Campo>
        </>
      )}
      <button className="primario" type="submit">{registro ? "Crear cuenta" : "Ingresar"}</button>
      <p className="enlaces">
        <Link className="link" to="/">Volver al inicio</Link>
        <button type="button" className="link" onClick={() => { setErr({}); setModo(registro ? "login" : "registro"); }}>
          {registro ? "Ya tengo cuenta" : "Crear cuenta"}
        </button>
      </p>
    </form>
    </div>
  );
}
