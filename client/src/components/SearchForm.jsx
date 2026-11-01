import { useState } from "react";

/**
 * The username box and Analyze button.
 * Props (inputs from the parent component):
 *   onSearch(username)  called when the form is submitted
 *   disabled            true while an analysis is running
 */
export default function SearchForm({ onSearch, disabled }) {
  // state: a value React remembers between renders; changing it with setUsername re-draws the component
  const [username, setUsername] = useState("");

  function handleSubmit(event) {
    event.preventDefault(); // stop the browser's default "reload the page" on form submit
    const trimmed = username.trim();
    if (trimmed) onSearch(trimmed);
  }

  return (
    <form className="search" onSubmit={handleSubmit}>
      <label htmlFor="username">GitHub username</label>
      <div className="search-row">
        {/* a "controlled input": React state is the single source of truth for what's in the box */}
        <input
          id="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="e.g. octocat"
          autoComplete="off"
          spellCheck={false}
        />
        <button type="submit" disabled={disabled || !username.trim()}>
          {disabled ? "Analyzing…" : "Analyze"}
        </button>
      </div>
    </form>
  );
}
