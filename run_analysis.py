"""The bridge between the Node/Express server and our Python code.

Express runs:   python run_analysis.py <username>
This script fetches the user's GitHub data, analyzes it, saves both JSON files,
and prints the results as ONE line of JSON to stdout. Express reads that line.

Rules of the contract with Node:
  - stdout gets ONLY the final JSON (progress messages go to stderr via log())
  - success -> exit code 0 and the results JSON
  - failure -> exit code 1 and {"error": "...", "code": "..."} so Node can pick the right HTTP status
    codes: bad_request | not_found | github_unavailable | github_error
"""
import sys
import json

from github_stats import check_user_exists, fetch_profile_data, save_raw_data
from analyze import analyze_profile, save_results


def fail(message, code):
    """Print an error as JSON to stdout and stop with exit code 1.
    message is for humans; code is a fixed word that programs (the Node server) can check."""
    print(json.dumps({"error": message, "code": code}))
    sys.exit(1) # a non-zero exit code is the standard way to tell the parent process "I failed"


def main():
    if len(sys.argv) < 2:
        fail("Usage: python run_analysis.py <username>", "bad_request")
    username = sys.argv[1].strip()

    # look the user up first: a 404 here means the username is wrong, which deserves its own message
    exists = check_user_exists(username)
    if exists is False: # "is False", not "not exists": None (unknown) must NOT land here
        fail(f"GitHub user '{username}' does not exist.", "not_found")
    if exists is None:
        fail("Could not reach GitHub. Try again in a minute.", "github_unavailable")

    repos = fetch_profile_data(username)
    if repos is None:
        fail(f"GitHub returned an error while fetching repos for '{username}'.", "github_error")

    save_raw_data(username, repos)
    results = analyze_profile(username, repos)
    save_results(username, results)

    print(json.dumps(results)) # one line of JSON on stdout: this is what Express receives


if __name__ == "__main__":
    main()
