// The Express API server.
// GET /api/analyze/:username  ->  analysis results as JSON (cached for a while)
// GET /api/health             ->  {"status": "ok", ...}
//
// Start it from the server/ folder with:  npm run dev   (restarts on every file save)
//                                     or:  npm start

import express from "express"; // the web framework: routes, requests, responses
import { runAnalysis } from "./analyzer.js"; // "./" = a file of ours, not a package from node_modules
import { TtlCache } from "./cache.js";

// settings that can be overridden by environment variables, with sensible defaults
const PORT = process.env.PORT || 3000;
const CACHE_TTL_MINUTES = Number(process.env.CACHE_TTL_MINUTES || 60);
const ANALYSIS_TIMEOUT_SECONDS = Number(process.env.ANALYSIS_TIMEOUT_SECONDS || 120);

// GitHub usernames: 1-39 letters, digits or hyphens, and they can't start with a hyphen
const USERNAME_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,38}$/;

// which HTTP status to send for each error code coming from the analyzer
const STATUS_BY_CODE = {
  bad_request: 400, // the request itself is wrong
  not_found: 404, // no such GitHub user
  github_error: 502, // GitHub answered, but with an error ("bad gateway")
  github_unavailable: 503, // couldn't reach GitHub at all ("service unavailable")
  timeout: 504, // GitHub/Python took too long ("gateway timeout")
  server_error: 500, // a bug or crash on our side
};

const cache = new TtlCache(CACHE_TTL_MINUTES * 60 * 1000); // minutes -> milliseconds
const inFlight = new Map(); // username -> Promise of an analysis that is running right now

/**
 * Analyze a user, but never run two analyses of the same user at the same time:
 * if one is already running, everyone who asks shares its Promise.
 * Successful results are stored in the cache.
 */
function analyzeOnce(key, username) {
  if (inFlight.has(key)) {
    return inFlight.get(key);
  }

  const promise = runAnalysis(username, { timeoutMs: ANALYSIS_TIMEOUT_SECONDS * 1000 })
    .then((results) => {
      cache.set(key, results); // only successes are cached; errors are retried next time
      return results;
    })
    .finally(() => {
      inFlight.delete(key); // runs after success OR failure: this analysis is no longer running
    });

  inFlight.set(key, promise);
  return promise;
}

const app = express();

// a tiny "is the server alive?" route, handy for checking the server and later for the deploy host
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", cachedProfiles: cache.size, running: inFlight.size });
});

// the main route: :username is a "route parameter", available as req.params.username
app.get("/api/analyze/:username", async (req, res) => {
  const { username } = req.params; // destructuring: same as const username = req.params.username

  // reject bad input before starting Python at all
  if (!USERNAME_PATTERN.test(username)) {
    return res.status(400).json({ error: "That is not a valid GitHub username.", code: "bad_request" });
  }

  // GitHub usernames are case-insensitive, so "Octocat" and "octocat" share one cache entry
  const key = username.toLowerCase();
  // ?refresh=true in the URL skips the cache and fetches fresh data
  const refresh = req.query.refresh === "true";

  if (!refresh) {
    const cached = cache.get(key);
    if (cached) {
      res.set("X-Cache", "HIT"); // a response header that says "this came from the cache"
      return res.json(cached);
    }
  }

  try {
    const results = await analyzeOnce(key, username); // wait for Python without blocking other requests
    res.set("X-Cache", "MISS");
    res.json(results); // status 200 + the results as JSON
  } catch (err) {
    const status = STATUS_BY_CODE[err.code] || 500;
    console.error(`Analysis failed for ${username} (${status}):`, err.message);
    res.status(status).json({ error: err.message, code: err.code || "server_error" });
  }
});

// any other /api/... path: answer with JSON instead of Express's default HTML error page
app.use("/api", (req, res) => {
  res.status(404).json({ error: `No route for ${req.method} ${req.originalUrl}`, code: "not_found" });
});

// error-handling middleware: Express recognizes it by its FOUR parameters.
// It catches anything a route throws that wasn't handled, so the server answers instead of hanging.
app.use((err, req, res, next) => {
  console.error("Unexpected error:", err);
  res.status(err.status || 500).json({ error: "Something went wrong on the server.", code: "server_error" });
});

// start listening for HTTP requests
app.listen(PORT, () => {
  console.log(`API running on http://localhost:${PORT}`);
  console.log(`Cache: ${CACHE_TTL_MINUTES} min, analysis timeout: ${ANALYSIS_TIMEOUT_SECONDS} s`);
});
