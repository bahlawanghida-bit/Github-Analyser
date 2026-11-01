import { useEffect, useState } from "react";
import { fetchAnalysis } from "./api.js";
import SearchForm from "./components/SearchForm.jsx";
import ProfileSummary from "./components/ProfileSummary.jsx";

/**
 * The top-level component. It owns the app's state and decides what to show:
 * nothing yet, a loading message, an error, or the results.
 */
export default function App() {
  // status is one of: "idle" | "loading" | "success" | "error"
  const [status, setStatus] = useState("idle");
  const [results, setResults] = useState(null);
  const [fromCache, setFromCache] = useState(false);
  const [error, setError] = useState("");

  async function analyze(username, options) {
    setStatus("loading");
    setError("");
    try {
      const { data, fromCache } = await fetchAnalysis(username, options);
      setResults(data);
      setFromCache(fromCache);
      setStatus("success");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  // useEffect runs code AFTER React has drawn the screen ("side effects": things outside React).
  // The [results] list means: run again only when results changes.
  useEffect(() => {
    document.title = results ? `${results.username} · GitHub Judger` : "GitHub Judger";
  }, [results]);

  return (
    <main className="app">
      <h1>GitHub Judger</h1>
      <p className="muted">See languages, activity and coding habits from any public GitHub profile.</p>

      <SearchForm onSearch={analyze} disabled={status === "loading"} />

      {/* conditional rendering: `condition && <X />` shows X only when the condition is true */}
      {status === "loading" && (
        <p className="notice">Fetching data from GitHub… the first analysis of a user can take up to a minute.</p>
      )}
      {status === "error" && <p className="notice error">{error}</p>}
      {status === "success" && (
        <ProfileSummary
          results={results}
          fromCache={fromCache}
          onRefresh={() => analyze(results.username, { refresh: true })}
        />
      )}
    </main>
  );
}
