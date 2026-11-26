import { useEffect, useState } from "react";
import { Link, useBlocker } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { Campo, errMap, focusCampo, useToast } from "../ui.jsx";

// Account details and password changes are kept in separate, authenticated forms.
export default function Perfil() {
  const { user, login } = useAuth();
  const toast = useToast();
  const nombre = user?.nombre || user?.correo?.split("@")[0] || "Usuario";
  const iniciales = nombre.split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
  const [perfil, setPerfil] = useState({ nombre, correo: user?.correo || "" });
  const [error, setError] = useState({});
  const [guardandoPerfil, setGuardandoPerfil] = useState(false);
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [password, setPassword] = useState({ nueva: "", repetir: "" });
  const [errorPassword, setErrorPassword] = useState({});
  const [guardandoPassword, setGuardandoPassword] = useState(false);
  const coincide = password.nueva.length >= 8 && password.nueva === password.repetir;
  const perfilModificado = perfil.nombre !== nombre || perfil.correo !== (user?.correo || "");
  const cambiosPendientes = perfilModificado || Boolean(password.nueva || password.repetir);
  const blocker = useBlocker(cambiosPendientes);

  useEffect(() => {
    if (!cambiosPendientes) return undefined;
    if (blocker.state === "blocked") {
      if (window.confirm("¿Está seguro que desea salir? No ha guardado los cambios en el perfil.")) blocker.proceed();
      else blocker.reset();
    }
    const confirmarSalida = (event) => {
      const elemento = event.target instanceof Element ? event.target : null;
      if (!elemento || elemento.closest(".tema-widget")) return;
      const control = elemento.closest("button");
      if (!control || control.matches('button[type="submit"]')) return;
      if (!window.confirm("¿Está seguro que desea salir? No ha guardado los cambios en el perfil.")) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    };
    const advertirRecarga = (event) => {
      event.preventDefault();
      event.returnValue = "";
    };
    document.addEventListener("click", confirmarSalida, true);
    window.addEventListener("beforeunload", advertirRecarga);
    return () => {
      document.removeEventListener("click", confirmarSalida, true);
      window.removeEventListener("beforeunload", advertirRecarga);
    };
  }, [blocker.state, blocker.proceed, blocker.reset, cambiosPendientes]);

  const cambiarPerfil = (campo) => (e) => {
    setPerfil((actual) => ({ ...actual, [campo]: e.target.value }));
    setError((actual) => ({ ...actual, [campo]: undefined, general: undefined }));
  };

  async function guardarPerfil(e) {
    e.preventDefault();
    setError({});
    setGuardandoPerfil(true);
    try {
      const resultado = await api("/auth/perfil", { method: "PATCH", body: perfil });
      login({ ...user, nombre: resultado.nombre, correo: resultado.correo });
      setPerfil({ nombre: resultado.nombre, correo: resultado.correo });
      toast(resultado.mensaje);
    } catch (e) {
      const errores = errMap(e);
      if (!Object.keys(errores).length) errores.general = e.detail;
      setError(errores);
      const primero = Object.keys(errores).find((campo) => campo !== "general");
      if (primero) setTimeout(() => focusCampo(primero), 0);
    } finally { setGuardandoPerfil(false); }
  }

  async function guardarPassword(e) {
    e.preventDefault();
    setErrorPassword({});
    if (!coincide) {
      setErrorPassword({ repetir: "Escribe la misma contraseña en ambos campos y usa al menos 8 caracteres." });
      return;
    }
    setGuardandoPassword(true);
    try {
      const resultado = await api("/auth/perfil/password", {
        method: "PUT",
        body: { password: password.nueva, repetir: password.repetir },
      });
      setPassword({ nueva: "", repetir: "" });
      setMostrarPassword(false);
      toast(resultado.mensaje);
    } catch (e) {
      const errores = errMap(e);
      if (!Object.keys(errores).length) errores.general = e.detail;
      setErrorPassword(errores);
    } finally { setGuardandoPassword(false); }
  }

  return (
    <section className="perfil-boceto">
      <div className="perfil-boceto__encabezado">
        <span className="portada__etiqueta">CUENTA</span>
        <h1>Mi perfil</h1>
        <p>Administra la información asociada a tu cuenta.</p>
      </div>
      <article className="perfil-identidad tarjeta">
        <div className="perfil-identidad__avatar" aria-hidden="true">{iniciales}</div>
        <div><h2>{perfil.nombre || nombre}</h2><p>{perfil.correo}</p><span className="estado">{user?.rol}</span></div>
      </article>
      <div className="perfil-cuadricula">
        <article className="tarjeta perfil-seccion perfil-seccion--wide">
          <span className="perfil-seccion__icono" aria-hidden="true">01</span>
          <h2>Información personal</h2>
          <p>Actualiza el nombre que aparece en tu cuenta y tu correo institucional.</p>
          <form onSubmit={guardarPerfil} noValidate>
            {error.general && <p className="msg" role="alert">{error.general}</p>}
            <Campo nombre="nombre" etiqueta="Nombre de usuario" error={error.nombre}>
              <input id="nombre" data-campo="nombre" value={perfil.nombre} onChange={cambiarPerfil("nombre")} autoComplete="username" required />
            </Campo>
            <Campo nombre="correo" etiqueta="Correo institucional" error={error.correo}>
              <input id="correo" data-campo="correo" type="email" value={perfil.correo} onChange={cambiarPerfil("correo")} autoComplete="email" required />
            </Campo>
            <button className="primario" type="submit" disabled={guardandoPerfil}>{guardandoPerfil ? "Guardando…" : "Guardar cambios"}</button>
          </form>
        </article>
        <article className="tarjeta perfil-seccion">
          <span className="perfil-seccion__icono" aria-hidden="true">02</span>
          <h2>Seguridad</h2>
          <p>Cambia tu contraseña. La confirmación debe coincidir antes de guardar.</p>
          {!mostrarPassword ? (
            <button type="button" onClick={() => setMostrarPassword(true)}>Cambiar contraseña</button>
          ) : (
            <form className="perfil-cambio-clave" onSubmit={guardarPassword} noValidate>
              {errorPassword.general && <p className="msg" role="alert">{errorPassword.general}</p>}
              <Campo nombre="password" etiqueta="Nueva contraseña" error={errorPassword.password} ayuda="Mínimo 8 caracteres.">
                <input id="password" data-campo="password" type="password" value={password.nueva} onChange={(e) => { setPassword({ ...password, nueva: e.target.value }); setErrorPassword({}); }} autoComplete="new-password" required />
              </Campo>
              <Campo nombre="repetir" etiqueta="Repetir contraseña" error={errorPassword.repetir}>
                <input id="repetir" data-campo="repetir" type="password" value={password.repetir} onChange={(e) => { setPassword({ ...password, repetir: e.target.value }); setErrorPassword({}); }} autoComplete="new-password" required />
              </Campo>
              {password.repetir && <p className={`perfil-coincidencia${coincide ? " correcta" : ""}`} aria-live="polite">
                {coincide ? "✓ Las contraseñas coinciden." : "Las contraseñas aún no coinciden."}
              </p>}
              <div className="fila">
                <button className="primario" type="submit" disabled={!coincide || guardandoPassword}>{guardandoPassword ? "Guardando…" : "Guardar contraseña"}</button>
                <button type="button" onClick={() => { setMostrarPassword(false); setPassword({ nueva: "", repetir: "" }); setErrorPassword({}); }}>Cancelar</button>
              </div>
            </form>
          )}
        </article>
        <article className="tarjeta perfil-seccion">
          <span className="perfil-seccion__icono" aria-hidden="true">03</span>
          <h2>Tu actividad</h2>
          <p>Acceso rápido a tus reseñas y aportes.</p>
          <Link className="boton" to="/panel">Ver mi panel</Link>
        </article>
      </div>
    </section>
  );
}
