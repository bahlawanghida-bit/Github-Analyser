// Vite's settings. Vite is the dev server + build tool:
//  - `npm run dev`   serves the app with instant reload while you edit
//  - `npm run build` bundles everything into plain HTML/CSS/JS files in dist/ for deployment
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react"; // teaches Vite to understand JSX and React fast-refresh

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // the PROXY: when the browser asks the Vite server for /api/..., Vite forwards the request
    //  to the Express server on port 3000 and passes the answer back.
    // For the browser everything comes from ONE origin (localhost:5173), so no CORS setup is needed.
    proxy: {
      "/api": "http://localhost:3000",
    },
  },
});
