const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "") + "/api";

export const getSesion = () => {
  try { return JSON.parse(localStorage.getItem("sesion")); } catch { return null; }
};

export async function api(path, { method = "GET", body, blob } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  const s = getSesion();
  if (s) headers.Authorization = "Bearer " + s.access_token;
  let r;
  try {
    r = await fetch(BASE + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw { detail: "No se pudo conectar con el servidor (si es Render gratis, puede estar despertando: reintenta en 30 s).", errores: [] };
  }
  if (r.status === 401 && s && !path.startsWith("/auth")) {
    localStorage.removeItem("sesion");
    location.href = "/login";
  }
  if (!r.ok) {
    let d = {};
    try { d = await r.json(); } catch {}
    throw { detail: d.detail || "Ocurrió un error.", errores: d.errores || [] };
  }
  if (blob) return r.blob();
  return r.status === 204 ? null : r.json();
}