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

export default function App() {
  const { user, logout } = useAuth();
  const rol = user?.rol;
  return (
    <>
      <a href="#main" className="saltar">Saltar al contenido</a>
      <nav>
        <Link to="/">Inicio</Link>
        {rol === "ESTUDIANTE" && <Link to="/panel">Mi panel</Link>}
        {(rol === "MODERADOR" || rol === "ADMIN") && <Link to="/moderacion">Moderación</Link>}
        {rol === "DOCENTE" && <Link to="/metricas">Mis métricas</Link>}
        <Link to="/ayuda">Ayuda</Link>
        <span className="sp" />
        {user ? (
          <button onClick={logout}>Salir ({user.correo})</button>
        ) : (
          <Link to="/login">Ingresar</Link>
        )}
      </nav>
      <main id="main">
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/login" element={<Login />} />
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