import { createContext, useContext, useState } from "react";
import { Navigate } from "react-router-dom";
import { getSesion } from "./api.js";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getSesion());
  const login = (d) => { localStorage.setItem("sesion", JSON.stringify(d)); setUser(d); };
  const logout = () => { localStorage.removeItem("sesion"); setUser(null); };
  return <Ctx.Provider value={{ user, login, logout }}>{children}</Ctx.Provider>;
}

export function Protegida({ roles, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.rol)) return <Navigate to="/" replace />;
  return children;
}