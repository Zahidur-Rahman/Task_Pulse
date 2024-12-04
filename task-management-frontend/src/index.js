import React from "react";
import ReactDOM from "react-dom/client";



import App from "./App";
import { AuthProvider } from "./context/AuthProvider";

// Find the root element in the DOM
const rootElement = document.getElementById("root");

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
