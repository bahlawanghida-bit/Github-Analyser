import os # lets us read environment variables (like token)
import requests # lets us send HTTP requests to GitHub's API
from dotenv import load_dotenv # lets us load variables from a .env file
import time
import json


# Load the .env file so GITHUB_TOKEN becomes available
#  via os.environ
load_dotenv()
# Read the token out of the environment
token = os.environ.get("GITHUB_TOKEN")
# Stop early with a clear error if the token wasn't found,
#  instead of failing later with a confusing 401
if not token:
    raise SystemExit("GITHUB_TOKEN not found. Check your .env file.")

# Headers sent with every request:
# proves who we are (auth) and what format we want back
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}


def github_get(url, params=None):
    """Send one GET request to the GitHub API, waiting out the rate limit if needed.
    Returns the response, or None if the network failed."""
    while True:
        try:
            # timeout: give up after 30 sec instead of hanging forever on a dead connection
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            # RequestException is the parent of ConnectionError, Timeout, etc. — catches all network problems
            print(f"Network error for {url}: {e}")
            return None

        # .get() instead of [] so a missing header doesn't crash with KeyError
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            # X-RateLimit-Reset is the moment (in seconds since 1970) the limit refills
            reset_at = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset_at - time.time(), 0) + 1
            print(f"Rate limit used up, pausing {wait:.0f} sec until it resets . . .")
            time.sleep(wait)
            # 403/429 means GitHub refused THIS request, so send it again now that the limit has reset
            if response.status_code in (403, 429):
                continue
        return response


def fetch_all_pages(url, params=None):
    """Fetch every page of a GitHub list endpoint (repos, commits...).
    Returns the combined list, [] for an empty repo, or None if something failed."""
    all_items = []
    page = 1 # Tracks which page we're currently requesting
    while True:
        # copy the caller's params and add the paging ones, so we never change the caller's dict
        page_params = dict(params or {})
        page_params["per_page"] = 100
        page_params["page"] = page

        response = github_get(url, page_params)
        if response is None:
            return None
        # 409 = the repo exists but has no commits yet (never pushed to)
        if response.status_code == 409:
            return []
        # any other non-200 (404 user not found, 403 forbidden...) is a real error
        if response.status_code != 200:
            print(f"GitHub error {response.status_code} for {url}: {response.text[:200]}")
            return None

        items = response.json()
        all_items.extend(items)
        # fewer than 100 items means this was the last page — no need to ask for an empty one
        if len(items) < 100:
            return all_items
        page += 1


def fetch_repos(username):
    """Fetch every public repo of a GitHub user. Returns a list of repo dicts, or None on error."""
    return fetch_all_pages(f"https://api.github.com/users/{username}/repos")


def fetch_languages(repo):
    """Fetch the bytes-per-language breakdown of one repo. Returns a dict ({} on error)."""
    response = github_get(repo["languages_url"])
    if response is None or response.status_code != 200:
        print(f"Could not fetch languages for {repo['name']}, skipping")
        return {}
    return response.json()


def fetch_commit_dates(repo, username):
    """Fetch the dates of every commit this user made to one repo (all pages).
    Returns a list of ISO date strings, or None on error."""
    # "author" filter: only this user's commits. Without it, forks would count
    #  every commit the ORIGINAL authors ever made as if they were this user's
    commits = fetch_all_pages(f"{repo['api_url']}/commits", {"author": username})
    if commits is None:
        return None
    return [c["commit"]["author"]["date"] for c in commits]


def main():
    # Ask the user which GitHub account to analyze
    # .strip() removes accidental spaces/newlines around what they typed
    username = input("Enter the GitHub username: ").strip()
    if not username:
        raise SystemExit("No username entered.")

    all_repos = fetch_repos(username)
    if all_repos is None:
        raise SystemExit(f"Could not fetch repos for '{username}'.")
    print(f"Total repos found: {len(all_repos)}")

    # Build a clean, filtered version of each repo,
    # keeping only the fields we actually need
    filtered_repos = []
    for repo in all_repos:
        filtered_repos.append({
            "name": repo["name"],                       # repo name
            "stars": repo["stargazers_count"],          # star count
            "primary_language": repo["language"],       # GitHub's single "main" language
            "languages_url": repo["languages_url"],     # endpoint for full language breakdown
            "api_url": repo["url"],                     # API base for this repo (commits live under it)
            "is_fork": repo["fork"],                    # whether this repo is a fork of another
            "url": repo["html_url"],                    # link to the repo on github.com
        })

    # For each repo, fetch its full language breakdown and the user's commits, and attach them
    for repo in filtered_repos:
        repo["languages"] = fetch_languages(repo)
        print(f"Fetched languages for: {repo['name']}")

        commit_dates = fetch_commit_dates(repo, username)
        repo["commit_dates"] = commit_dates
        # None (fetch failed) stays None so the analysis knows the count is unknown, not zero
        repo["commit_count"] = len(commit_dates) if commit_dates is not None else None
        print(f"Fetched commits for: {repo['name']} - {repo['commit_count']}")

    os.makedirs("data", exist_ok=True) # create a folder called data
    output_filename = os.path.join("data", f"{username}_github_data.json") #create a file name using the username of the account inside the file "data"
    with open(output_filename, "w", encoding="utf-8") as f: #create or over write a file
        json.dump(filtered_repos, f, indent=2)

    print(f"Data saved to {output_filename}")


# Only run main() when this file is run directly (python github_stats.py),
#  not when another file imports it to reuse fetch_repos() etc.
if __name__ == "__main__":
    main()

#The with ... as f: pattern is important — it's called a context manager.
# It automatically closes the file for you once you're done
#  writing to it, even if an error happens partway through. f is
# just a variable name (short for "file") representing the open file,
