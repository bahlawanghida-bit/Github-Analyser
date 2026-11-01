import os
import sys # lets us read command-line arguments (sys.argv)
import pandas as pd
import json
from datetime import datetime, timezone # to stamp WHEN the analysis ran

# Monday..Sunday in calendar order, so day counts always come out in the same order
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_repo_data(username):
    """Read the raw data file that github_stats.py saved for this user.
    Returns the list of repo dicts, or None if the file doesn't exist yet."""
    data_filename = os.path.join("data", f"{username}_github_data.json") # the file name github_stats.py uses
    try:
        with open(data_filename, "r", encoding="utf-8") as f: # read a file
            return json.load(f)
    except FileNotFoundError:
        return None


def compute_language_totals(repos):
    """Add up the bytes of each language across all of the user's own repos (forks skipped).
    Returns a dict like {"Python": 12000, "HTML": 3000}."""
    language_totals = {}
    # empty dict to hold running byte totals per language, across all repos

    for repo in repos:
        # loop through every repo dict in the loaded data
        # forks are mostly someone else's code, so they don't count toward this user's languages
        if repo.get("is_fork"):
            continue
        for language_name, language_bytes in (repo.get("languages") or {}).items():
            # loop through each language in this repo, getting both its name and byte count
            # skip anything that isn't a byte count (old data files may hold an error message here)
            if not isinstance(language_bytes, int):
                continue
            language_totals[language_name] = language_totals.get(language_name, 0) + language_bytes
            # add this repo's byte count to the running total for that language (0 if first time seeing it)

    return language_totals


def compute_language_percentages(language_totals):
    """Turn byte totals into each language's share of all bytes, as a percentage (2 decimals).
    Returns a dict like {"Python": 80.0, "HTML": 20.0}."""
    lang_bytes_sum = sum(language_totals.values())
    # total bytes written across all languages combined

    language_percentages = {}
    for language_name, language_bytes in language_totals.items():
        # this language's percentage of total bytes, rounded to 2 decimal places
        language_percentages[language_name] = round((language_bytes / lang_bytes_sum) * 100, 2)

    return language_percentages


def find_most_active_repo(df):
    """Find the repo with the most commits by this user.
    Returns that repo's row (a pandas Series), or None if no repo has a known commit count."""
    # an account with no repos gives an empty DataFrame with NO columns at all,
    #  so df["commit_count"] would crash with KeyError: check the column exists first
    if "commit_count" not in df.columns:
        return None
    # .notna() -> True/False per repo, .any() -> True if at least one count is known
    # without this check, iloc[0] would pick a random repo whose count is unknown
    if not df["commit_count"].notna().any():
        return None

    sorted_df = df.sort_values("commit_count", ascending=False)
    # a NEW DataFrame sorted by commit_count, highest first (unknown counts go last); df itself is unchanged
    return sorted_df.iloc[0]
    # iloc[0] = the first row by POSITION, i.e. the repo with the highest commit_count


def collect_commit_dates(repos):
    """Flatten every repo's commit dates into one list of ISO date strings."""
    all_commit_dates = [] # empty list to hold every commit timestamp across all repos
    for repo in repos:
        if repo.get("commit_dates"): # skip repos whose commit fetch failed (None) or that have no commits ([])
            all_commit_dates.extend(repo["commit_dates"]) # add all of this repo's dates into the combined flat list
    return all_commit_dates


def analyze_commit_times(commit_dates):
    """Count commits per hour of day (UTC) and per weekday.
    Returns (commits_by_hour, commits_by_day, most_common_hour):
      commits_by_hour  a list of 24 ints, index 0 = midnight..1am, index 23 = 11pm..midnight
      commits_by_day   a dict {"Monday": n, ..., "Sunday": n} in calendar order
      most_common_hour the busiest hour (0-23), or None when there are no commits"""
    if not commit_dates:
        return [0] * 24, {day: 0 for day in WEEKDAYS}, None

    commit_datetimes = pd.to_datetime(commit_dates) # convert the raw ISO strings into real datetimes pandas understands

    hour_counts = commit_datetimes.hour.value_counts() # how many commits happened in each hour (only hours that occur)
    day_counts = commit_datetimes.day_name().value_counts() # how many commits happened on each weekday

    # turn the pandas results into plain Python lists/dicts, filling in 0 for hours/days with no commits
    # int(...) converts numpy's int64 into a normal int, which json.dump knows how to save
    commits_by_hour = [int(hour_counts.get(hour, 0)) for hour in range(24)]
    commits_by_day = {day: int(day_counts.get(day, 0)) for day in WEEKDAYS}

    most_common_hour = int(hour_counts.idxmax()) # idxmax = the LABEL (here: the hour) of the biggest count
    return commits_by_hour, commits_by_day, most_common_hour


def get_language_tag(language_count):
    """Name the user by how many distinct languages they use."""
    if language_count == 0:
        return "No Code Yet"
    elif language_count == 1:
        return "Monolingual"
    elif language_count == 2:
        return "Bilingual"
    elif language_count == 3:
        return "Trilingual"
    else:
        return "Polyglot"


def get_time_tag(most_common_hour):
    """Name the user by the hour (UTC) they commit most. None means no commits at all."""
    if most_common_hour is None:
        return "No Activity"
    # every hour 0-23 falls into exactly one tag
    if most_common_hour >= 22 or most_common_hour < 4:
        return "Night Owl"
    elif 4 <= most_common_hour <= 10:
        return "Early Bird"
    else:
        return "Regular Hour"


def analyze_profile(username, repos):
    """Run every analysis on one user's repos and gather the answers into one dict.
    Everything inside is a plain str/int/float/list/dict/None, so it can be saved as JSON
    and later sent by the Express API to the website."""
    df = pd.DataFrame(repos) # list of dicts -> table: each dict is a row, its keys become the column names

    language_totals = compute_language_totals(repos)
    language_percentages = compute_language_percentages(language_totals)

    most_active_row = find_most_active_repo(df)
    if most_active_row is None:
        most_active_repo = None
    else:
        # keep only the fields the dashboard needs; int() undoes pandas' float64 (12.0 -> 12)
        most_active_repo = {
            "name": most_active_row["name"],
            "commit_count": int(most_active_row["commit_count"]),
            "url": most_active_row["url"],
        }

    commit_dates = collect_commit_dates(repos)
    commits_by_hour, commits_by_day, most_common_hour = analyze_commit_times(commit_dates)
    # ^ "unpacking": the function returns 3 values at once and we name each one

    return {
        "username": username,
        # ISO 8601 time in UTC, e.g. "2026-11-01T14:03:22+00:00"; the website shows it as "last updated"
        "analyzed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_count": len(repos),
        "fork_count": sum(1 for repo in repos if repo.get("is_fork")), # count repos where is_fork is True
        "total_commits": len(commit_dates),
        "language_totals": language_totals,
        "language_percentages": language_percentages,
        "most_active_repo": most_active_repo,
        "commits_by_hour": commits_by_hour,
        "commits_by_day": commits_by_day,
        "most_common_hour_utc": most_common_hour,
        "tags": {
            "language": get_language_tag(len(language_totals)),
            "time": get_time_tag(most_common_hour),
        },
    }


def save_results(username, results):
    """Write the analysis results to data/<username>_results.json and return the file path."""
    os.makedirs("data", exist_ok=True)
    results_filename = os.path.join("data", f"{username}_results.json")
    with open(results_filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results_filename


def print_report(results):
    """Print the results in a human-friendly way for the terminal."""
    print(f"\n=== {results['username']} ===")
    print(f"Repos: {results['repo_count']} ({results['fork_count']} forks), commits: {results['total_commits']}")

    print("\nLanguages:")
    # sorted(..., key=..., reverse=True): biggest percentage first
    for language_name, percentage in sorted(results["language_percentages"].items(), key=lambda item: item[1], reverse=True):
        print(f"  {language_name:<15} {percentage:>6.2f}%")

    repo = results["most_active_repo"]
    if repo is None:
        print("\nMost active repo: unknown (no commit counts)")
    else:
        print(f"\nMost active repo: {repo['name']} ({repo['commit_count']} commits)")

    print("\nCommits per weekday:")
    for day, count in results["commits_by_day"].items():
        print(f"  {day:<10} {count}")

    print(f"\nBusiest hour (UTC): {results['most_common_hour_utc']}")
    print(f"Tags: {results['tags']['language']}, {results['tags']['time']}")


def main():
    # sys.argv is the list of words typed on the command line:
    #   python analyze.py octocat  ->  sys.argv == ["analyze.py", "octocat"]
    # use the username from there if given, otherwise ask for it
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    else:
        username = input("enter the github username: ").strip()

    repos = load_repo_data(username)
    if repos is None:
        raise SystemExit(f"No data file for '{username}'. Run github_stats.py for '{username}' first.")
    if not repos:
        raise SystemExit("This account has no public repos, nothing to analyze.")

    results = analyze_profile(username, repos)
    print_report(results)
    print(f"\nResults saved to {save_results(username, results)}")


if __name__ == "__main__":
    main()
