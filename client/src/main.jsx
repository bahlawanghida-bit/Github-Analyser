// The entry point: the first JavaScript file the browser runs.
// Its only job is to find <div id="root"> in index.html and draw <App /> inside it.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css"; // Vite lets JS import CSS; it injects the styles into the page

createRoot(document.getElementById("root")).render(
  // StrictMode adds extra checks in development (it runs some code twice to expose bugs); no effect in production
  <StrictMode>
    <App />
  </StrictMode>,
);
