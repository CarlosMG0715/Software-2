import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { Campo, errMap, focusCampo, useToast } from "../ui.jsx";

export default function Login() {
  const [modo, setModo] = useState("login"); // login | registro | token | recuperar | reset
  const [f, setF] = useState({ correo: "", password: "", acepta: false, token: "", nueva: "" });
  const [err, setErr] = useState({});
  const { login } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

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
      } else if (modo === "registro") {
        const r = await api("/auth/registrar", { method: "POST", body: { correo: f.correo, password: f.password, acepta_ley_1581: f.acepta } });
        setF({ ...f, token: r.token_dev || "" });
        toast(r.mensaje);
        setModo("token");
      } else if (modo === "token") {
        const r = await api("/auth/verificar-token", { method: "POST", body: { token: f.token } });
        toast(r.mensaje);
        setModo("login");
      } else if (modo === "recuperar") {
        const r = await api("/auth/recuperar-clave", { method: "POST", body: { correo: f.correo } });
        setF({ ...f, token: r.token_dev || "" });
        toast(r.mensaje);
        setModo("reset");
      } else {
        const r = await api("/auth/recuperar-clave", { method: "POST", body: { token: f.token, nueva_password: f.nueva } });
        toast(r.mensaje);
        setModo("login");
      }
    } catch (e) { fallo(e); }
  }

  const titulos = { login: "Ingresar", registro: "Crear cuenta", token: "Activar cuenta", recuperar: "Recuperar clave", reset: "Nueva contraseña" };
  return (
    <form onSubmit={enviar} className="tarjeta estrecha" noValidate>
      <h1>{titulos[modo]}</h1>
      {err.general && <p className="msg" role="alert">{err.general}</p>}
      {["login", "registro", "recuperar"].includes(modo) && (
        <Campo nombre="correo" etiqueta="Correo institucional" error={err.correo}>
          <input id="correo" data-campo="correo" type="email" value={f.correo} onChange={set("correo")} autoComplete="email" />
        </Campo>
      )}
      {["login", "registro"].includes(modo) && (
        <Campo nombre="password" etiqueta="Contraseña" error={err.password} ayuda={modo === "registro" ? "Mínimo 8 caracteres." : null}>
          <input id="password" data-campo="password" type="password" value={f.password} onChange={set("password")} autoComplete={modo === "login" ? "current-password" : "new-password"} />
        </Campo>
      )}
      {modo === "registro" && (
        <Campo nombre="acepta_ley_1581" error={err.acepta_ley_1581} etiqueta="">
          <label className="check">
            <input id="acepta_ley_1581" data-campo="acepta_ley_1581" type="checkbox" checked={f.acepta} onChange={set("acepta")} />
            Autorizo el tratamiento de mis datos personales (Ley 1581 de 2012).
          </label>
        </Campo>
      )}
      {["token", "reset"].includes(modo) && (
        <Campo nombre="token" etiqueta="Token recibido por correo" error={err.token}>
          <input id="token" data-campo="token" value={f.token} onChange={set("token")} />
        </Campo>
      )}
      {modo === "reset" && (
        <Campo nombre="nueva_password" etiqueta="Nueva contraseña" error={err.nueva_password}>
          <input id="nueva_password" data-campo="nueva_password" type="password" value={f.nueva} onChange={set("nueva")} autoComplete="new-password" />
        </Campo>
      )}
      <button className="primario" type="submit">{titulos[modo]}</button>
      <p className="enlaces">
        {modo !== "login" && <button type="button" className="link" onClick={() => setModo("login")}>Ya tengo cuenta</button>}
        {modo === "login" && <button type="button" className="link" onClick={() => setModo("registro")}>Crear cuenta</button>}
        {modo === "login" && <button type="button" className="link" onClick={() => setModo("recuperar")}>Olvidé mi clave</button>}
      </p>
    </form>
  );
}