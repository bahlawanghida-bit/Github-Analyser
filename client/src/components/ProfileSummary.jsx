/**
 * Shows the analysis results. Charts come in D6; for now: tags, numbers, simple bars and lists.
 * Props: results (the JSON from the API), fromCache (bool), onRefresh() to fetch fresh data.
 */
export default function ProfileSummary({ results, fromCache, onRefresh }) {
  // turn {"Java": 26.35, "HTML": 20.75, ...} into [["Java", 26.35], ...] sorted biggest first
  const languages = Object.entries(results.language_percentages).sort((a, b) => b[1] - a[1]);
  const repo = results.most_active_repo;
  // new Date(isoText) parses the timestamp; toLocaleString shows it in the viewer's own time zone and format
  const analyzedAt = new Date(results.analyzed_at).toLocaleString();

  return (
    <section className="summary">
      <header className="summary-header">
        <h2>
          <a href={`https://github.com/${results.username}`} target="_blank" rel="noreferrer">
            {results.username}
          </a>
        </h2>
        <p className="muted">
          Analyzed {analyzedAt}
          {fromCache && " (cached)"}{" "}
          <button className="link-button" onClick={onRefresh}>
            Refresh
          </button>
        </p>
        <div className="tags">
          <span className="tag">{results.tags.language}</span>
          <span className="tag">{results.tags.time}</span>
        </div>
      </header>

      <div className="stats">
        <Stat label="Repos" value={results.repo_count} />
        <Stat label="Forks" value={results.fork_count} />
        <Stat label="Commits" value={results.total_commits} />
        <Stat label="Busiest hour (UTC)" value={results.most_common_hour_utc ?? "–"} />
      </div>

      <h3>Languages</h3>
      {languages.length === 0 ? (
        <p className="muted">No code found in this account's own repos.</p>
      ) : (
        <ul className="bars">
          {/* .map turns each data item into a piece of UI; "key" helps React track list items */}
          {languages.map(([name, percent]) => (
            <li key={name}>
              <span className="bar-label">{name}</span>
              <span className="bar-track">
                <span className="bar-fill" style={{ width: `${percent}%` }} />
              </span>
              <span className="bar-value">{percent.toFixed(1)}%</span>
            </li>
          ))}
        </ul>
      )}

      <h3>Most active repo</h3>
      {repo ? (
        <p>
          <a href={repo.url} target="_blank" rel="noreferrer">
            {repo.name}
          </a>{" "}
          with {repo.commit_count} commits
        </p>
      ) : (
        <p className="muted">Unknown (no commit counts).</p>
      )}

      <h3>Commits per weekday</h3>
      <ul className="days">
        {Object.entries(results.commits_by_day).map(([day, count]) => (
          <li key={day}>
            <span>{day.slice(0, 3)}</span>
            <strong>{count}</strong>
          </li>
        ))}
      </ul>
    </section>
  );
}

/** A small reusable box: a big number with a label under it. */
function Stat({ label, value }) {
  return (
    <div className="stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
