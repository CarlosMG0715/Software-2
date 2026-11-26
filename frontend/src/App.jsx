import { useEffect, useRef, useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import { Protegida, useAuth } from "./auth.jsx";
import Login from "./pages/Login.jsx";
import Inicio from "./pages/Inicio.jsx";
import Docente from "./pages/Docente.jsx";
import Asignatura from "./pages/Asignatura.jsx";
import ResenaForm from "./pages/ResenaForm.jsx";
import Panel from "./pages/Panel.jsx";
import Moderacion from "./pages/Moderacion.jsx";
import Metricas from "./pages/Metricas.jsx";
import Ayuda from "./pages/Ayuda.jsx";
import Perfil from "./pages/Perfil.jsx";

export default function App() {
  const { user, logout } = useAuth();
  // System mode leaves the theme attribute unset so CSS can follow the OS preference.
  const [tema, setTema] = useState(() => {
    try {
      const guardado = localStorage.getItem("tema");
      return ["claro", "oscuro", "sistema"].includes(guardado) ? guardado : "sistema";
    } catch { return "sistema"; }
  });
  const [ruedaAbierta, setRuedaAbierta] = useState(false);
  const ruedaRef = useRef(null);
  const botonTemaRef = useRef(null);
  const [menuCuentaAbierto, setMenuCuentaAbierto] = useState(false);
  const menuCuentaRef = useRef(null);
  const botonCuentaRef = useRef(null);
  useEffect(() => {
    if (tema === "sistema") document.documentElement.removeAttribute("data-tema");
    else document.documentElement.dataset.tema = tema;
    try { localStorage.setItem("tema", tema); } catch { /* Storage may be unavailable. */ }
  }, [tema]);
  useEffect(() => {
    if (!ruedaAbierta) return undefined;
    const cerrarFuera = (event) => {
      if (!ruedaRef.current?.contains(event.target)) setRuedaAbierta(false);
    };
    const cerrarEscape = (event) => {
      if (event.key === "Escape") {
        setRuedaAbierta(false);
        botonTemaRef.current?.focus();
      }
    };
    document.addEventListener("pointerdown", cerrarFuera);
    document.addEventListener("keydown", cerrarEscape);
    return () => {
      document.removeEventListener("pointerdown", cerrarFuera);
      document.removeEventListener("keydown", cerrarEscape);
    };
  }, [ruedaAbierta]);
  useEffect(() => {
    if (!menuCuentaAbierto) return undefined;
    const cerrarFuera = (event) => {
      if (!menuCuentaRef.current?.contains(event.target)) setMenuCuentaAbierto(false);
    };
    const cerrarEscape = (event) => {
      if (event.key === "Escape") {
        setMenuCuentaAbierto(false);
        botonCuentaRef.current?.focus();
      }
    };
    document.addEventListener("pointerdown", cerrarFuera);
    document.addEventListener("keydown", cerrarEscape);
    return () => {
      document.removeEventListener("pointerdown", cerrarFuera);
      document.removeEventListener("keydown", cerrarEscape);
    };
  }, [menuCuentaAbierto]);
  const rol = user?.rol;
  const nombreVisible = user?.nombre || user?.correo?.split("@")[0] || "Mi cuenta";
  const opcionesTema = [
    { value: "claro", label: "Modo claro", icon: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" /></> },
    { value: "oscuro", label: "Modo oscuro", icon: <path d="M20.8 14.2A8.5 8.5 0 0 1 9.8 3.2 8.5 8.5 0 1 0 20.8 14.2Z" /> },
    { value: "sistema", label: "Por Defecto del sistema", icon: <><rect x="3" y="4" width="18" height="13" rx="2" /><path d="M8 21h8m-4-4v4" /></> },
  ];
  const temaActivo = opcionesTema.find((opcion) => opcion.value === tema) || opcionesTema[2];
  return (
    <>
      <a href="#main" className="saltar">Saltar al contenido</a>
      <nav>
        <Link className="nav-link" to="/">{rol === "ESTUDIANTE" ? "Reseñar" : "Profesores"}</Link>
        {rol === "ESTUDIANTE" && <Link to="/panel">Mi panel</Link>}
        {(rol === "MODERADOR" || rol === "ADMIN") && <Link to="/moderacion">Moderación</Link>}
        {rol === "DOCENTE" && <Link to="/metricas">Mis métricas</Link>}
        <Link className="nav-link" to="/ayuda">Ayuda</Link>
        <span className="sp" />
        {user ? (
          <div className={`cuenta-nav${menuCuentaAbierto ? " abierta" : ""}`} ref={menuCuentaRef}>
            <button
              ref={botonCuentaRef}
              className="cuenta-nav__toggle"
              type="button"
              aria-haspopup="menu"
              aria-expanded={menuCuentaAbierto}
              onClick={() => setMenuCuentaAbierto((abierto) => !abierto)}
            >
              <svg className="cuenta-nav__persona" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5" /><path d="M4.5 21a7.5 7.5 0 0 1 15 0" /></svg>
              <span className="cuenta-nav__nombre">{nombreVisible}</span>
              <svg className="cuenta-nav__hamburguesa" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
            </button>
            {menuCuentaAbierto && <div className="cuenta-nav__menu" role="menu">
              <Link role="menuitem" to="/perfil" onClick={() => setMenuCuentaAbierto(false)}>Ver perfil</Link>
              <button role="menuitem" type="button" className="cuenta-nav__salir" onClick={() => { setMenuCuentaAbierto(false); logout(); }}>Salir</button>
            </div>}
          </div>
        ) : (
          <Link className="ingresar" to="/login">Ingresar</Link>
        )}
      </nav>
      <main id="main">
        <div className={`tema-widget${ruedaAbierta ? " abierta" : ""}`} ref={ruedaRef}>
          <div id="tema-rueda" className="tema-rueda" role="group" aria-label="Cambiar tema" aria-hidden={!ruedaAbierta}>
            {opcionesTema.map(({ value, label, icon }) => (
              <button
                key={value}
                className={`tema-opcion${tema === value ? " activa" : ""}`}
                type="button"
                aria-label={label}
                aria-pressed={tema === value}
                data-tooltip={label}
                tabIndex={ruedaAbierta ? 0 : -1}
                onClick={() => { setTema(value); setRuedaAbierta(false); botonTemaRef.current?.focus(); }}
              >
                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{icon}</svg>
              </button>
            ))}
          </div>
          <button
            ref={botonTemaRef}
            className="tema-toggle"
            type="button"
            aria-label={ruedaAbierta ? "Cerrar opciones de tema" : `Tema seleccionado: ${temaActivo.label}. Abrir opciones de tema`}
            aria-expanded={ruedaAbierta}
            aria-controls="tema-rueda"
            data-tooltip={temaActivo.label}
            onClick={() => setRuedaAbierta((abierta) => !abierta)}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{temaActivo.icon}</svg>
          </button>
        </div>
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/login" element={<Login />} />
          <Route path="/perfil" element={<Protegida><Perfil /></Protegida>} />
          <Route path="/docentes/:id" element={<Docente />} />
          <Route path="/asignaturas/:codigo" element={<Asignatura />} />
          <Route path="/ayuda" element={<Ayuda />} />
          <Route path="/resena/nueva/:docenteId" element={<Protegida roles={["ESTUDIANTE"]}><ResenaForm /></Protegida>} />
          <Route path="/resena/editar/:id" element={<Protegida roles={["ESTUDIANTE"]}><ResenaForm /></Protegida>} />
          <Route path="/panel" element={<Protegida roles={["ESTUDIANTE"]}><Panel /></Protegida>} />
          <Route path="/moderacion" element={<Protegida roles={["MODERADOR", "ADMIN"]}><Moderacion /></Protegida>} />
          <Route path="/metricas" element={<Protegida roles={["DOCENTE"]}><Metricas /></Protegida>} />
          <Route path="*" element={<p>Página no encontrada.</p>} />
        </Routes>
      </main>
    </>
  );
}
