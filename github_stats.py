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
    raise SystemExit("GITHUB_TOKEN not found. Check you .env file.")

# Headers sent with every request: 
# proves who we are (auth) and what format we want back
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}
# Ask the user which GitHub account to analyze
username = input("Enter the GitHub username: ")
# Build the URL for this user's repo list
repos_url= f"https://api.github.com/users/{username}/repos"
# Will hold every repo across all pages combined
all_repos = []

page = 1 # Tracks which page we're currently requesting
# Keep requesting pages until GitHub returns
# an empty page (no more repos left)
while True:
      # Ask for up to 100 repos on the current page
    response = requests.get(repos_url, headers=headers,params={"per_page": 100, "page": page})
    repos = response.json()
      
    print(f"Page {page}: status {response.status_code}, got {len(repos) if isinstance(repos, list) else 'ERROR'} items")
    # Empty list means we've gone past 
    # the last real page — stop looping
    if not repos:
        break
    # Add this page's repos into our running total list
    all_repos.extend(repos)
    page+=1


print (f"Total repos found: {len(all_repos)}")
# Build a clean, filtered version of each repo, 
# keeping only the fields we actually need
filtered_repos = []
for repo in all_repos :
    filtered_repos.append({
       "name": repo["name"],                      # repo name
        "stars": repo["stargazers_count"],          # star count
        "primary_language": repo["language"],       # GitHub's single "main" language
        "languages_url": repo["languages_url"],     # endpoint for full language breakdown
        "is_fork": repo["fork"],                     # whether this repo is a fork of another
        "url": repo["html_url"],                     # link to the repo on github.com
    })
# For each repo, fetch its full 
# language breakdown (bytes per language) and attach it
for repo in filtered_repos :
    try:
        lang_response = requests.get(repo["languages_url"], headers= headers)
        # add a new "languages" key into this repo's dict
        repo["languages"] = lang_response.json()
    except requests.exceptions.ConnectError:
        print(f"Connection Error fetching languages for {repo['name']},skippig")
        repo["languages"]= {}   
     # progress indicator so we can see it working
    print(f"Fetched languages for: {repo['name']}")

    try:
        commits_url = repo["languages_url"].replace("/languages","/commits")
        commits_response = requests.get(commits_url, headers= headers, params= {"per_page": 100})
        commitsList = commits_response.json()
        commit_count = len(commitsList)
        commit_dates = [c["commit"]["author"]["date"] for c in commitsList]
        repo["commit_count"]= commit_count
        repo["commit_dates"]= commit_dates
        #get  the meta data rate limit from the header than convert it to an int
        remaining = int(commits_response.headers["X-RateLimit-Remaining"])
        print(f"Rate Limit Remaining: {remaining}")
        if remaining < 10:
            print("Rate Limit low, pausing for 60 sec . . .")
            time.sleep(60)
    except requests.exceptions.ConnectionError:
            print(f"connection Error fetching commits for {repo['name']}, skipping.")
            repo["commit_count"] = None
            repo["commit_dates"] = None
            commit_count = None
            commit_dates = None

    print(f"fetched commits for: {repo['name']} - {commit_count}")


    

os.makedirs("data", exist_ok=True) # create a folder called data
output_filename = os.path.join("data", f"{username}_github_data.json") #create a file name using the username of the account inside the file "data"
with open(output_filename, "w") as f: #create or over write a file 
    json.dump(filtered_repos, f, indent=2)

print(f"Data saved to {output_filename}")

#The with ... as f: pattern is important — it's called a context manager. 
# It automatically closes the file for you once you're done
#  writing to it, even if an error happens partway through. f is 
# just a variable name (short for "file") representing the open file, 

