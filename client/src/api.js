// Every call from the website to our Express API goes through this file,
// so components never deal with URLs, status codes or JSON parsing themselves.

/**
 * Ask the API to analyze a GitHub user.
 * Resolves with { data, fromCache }, or throws an Error whose message can be shown to the user.
 */
export async function fetchAnalysis(username, { refresh = false } = {}) {
  // encodeURIComponent makes any text safe to put inside a URL ("a b" -> "a%20b")
  const url = `/api/analyze/${encodeURIComponent(username)}${refresh ? "?refresh=true" : ""}`;

  let response;
  try {
    response = await fetch(url); // fetch = the browser's built-in way to send HTTP requests
  } catch {
    // fetch only throws when there is no answer at all (network down)
    throw new Error("Can't reach the server. Check your connection.");
  }

  // .json() fails if the body isn't JSON; .catch turns that failure into null instead of crashing
  const data = await response.json().catch(() => null);

  if (!data) {
    // the Vite proxy answers with a non-JSON error page when Express isn't running
    throw new Error("The API server isn't answering. Start it with `npm run dev` in the server folder.");
  }
  // response.ok is true for status 200-299
  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }

  return { data, fromCache: response.headers.get("X-Cache") === "HIT" };
}
