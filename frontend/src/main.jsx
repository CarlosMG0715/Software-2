import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider } from "./auth.jsx";
import { ToastProvider } from "./ui.jsx";
import "./styles/index.css";

const router = createBrowserRouter([{ path: "*", element: <App /> }]);

createRoot(document.getElementById("root")).render(
  <ToastProvider>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </ToastProvider>
);
