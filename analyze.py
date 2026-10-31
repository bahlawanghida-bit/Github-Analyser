import os
import pandas as pd
import json


def main():
    username = input("enter the github username: ").strip()
    output_filename = os.path.join("data", f"{username}_github_data.json") #create a file name using the username of the account inside the file "data"
    try:
        with open(output_filename, "r", encoding="utf-8") as f: #read a file
            output = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"No data file at {output_filename}. Run github_stats.py for '{username}' first.")

    print(f"Data loaded from {output_filename}")

    if not output:
        raise SystemExit("This account has no public repos, nothing to analyze.")

    df = pd.DataFrame(output) # turn list of dictionary into tables for data each dict is a row, and each dict's keys become column names.
    print(df)

    language_totals = {}
    # empty dict to hold running byte totals per language, across all repos

    for repo in output:
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

    print(language_totals)
    # check: raw byte totals per language across the whole account

    lang_bytes_sum = sum(language_totals.values())
    # total bytes written across all languages combined

    language_percentages = {}
    # empty dict to hold each language's share of total bytes, as a percentage

    for language_name, language_bytes in language_totals.items():
        # loop through the totals we just calculated
        language_percentages[language_name] = round((language_bytes / lang_bytes_sum) * 100, 2)
        # this language's percentage of total bytes, rounded to 2 decimal places

    print(language_percentages)
    # check: percentage breakdown per language

    # only rank repos if at least one has a known commit count, otherwise iloc[0] would pick a random repo
    if df["commit_count"].notna().any():
        sorted_df = df.sort_values("commit_count", ascending=False)# sort all repos by commit_count, highest first (unknown counts go last)
        print(sorted_df[["name", "commit_count"]])# check: repos sorted by commit_count, highest first — only showing name and count for readability
        most_active_repo = sorted_df.iloc[0]# grab the very first row of the sorted DataFrame — the repo with the highest commit_count
        print(most_active_repo)# check: details of the single most active repo
    else:
        print("No commit counts available, can't pick a most active repo.")

    all_commit_dates = []# empty list to hold every commit timestamp across all repos, flattened into one list

    for repo in output:# loop through every repo dict
        if repo.get("commit_dates"): # skip repos whose commit fetch failed (None) or that have no commits ([])
            all_commit_dates.extend(repo["commit_dates"]) # add all of this repo's commit dates into the combined flat list

    print(len(all_commit_dates))# check: total number of commits across the whole account

    language_count = len(language_totals)# count how many distinct languages appear across the whole account
    print(language_count)# check: total number of distinct languages used

    if language_count == 0:
        language_tag = "No Code Yet"
    elif language_count == 1:
        language_tag = "Monolingual"
    elif language_count == 2:
        language_tag = "Bilingual"
    elif language_count == 3:
        language_tag = "Trilingual"
    else:
        language_tag = "Polyglot"

    print(language_tag)

    # with no commits there are no hours/days to analyze (and hour_counts.index[0] would crash)
    if not all_commit_dates:
        print("No commits found, skipping time analysis.")
        time_tag = "No Activity"
    else:
        commit_datetimes = pd.to_datetime(all_commit_dates) # convert the raw ISO date strings into real datetime objects pandas can analyze
        print(commit_datetimes)# check: see the converted datetime values

        commit_hours = commit_datetimes.hour# extract just the hour (0-23) from each commit's datetime
        print(commit_hours)# check: see all the hours commits happened at

        hour_counts = commit_hours.value_counts()# count how many commits happened during each hour, across the whole account
        print(hour_counts)# check: commit frequency by hour of day

        commit_days = commit_datetimes.day_name()# extract the day of the week (e.g. "Monday") from each commit's datetime
        print(commit_days)# check: see all the days commits happened on
        day_counts = commit_days.value_counts()# count how many commits happened on each day of the week
        print(day_counts)

        most_common_hour = hour_counts.index[0]# get the hour with the highest number of commits
        print(most_common_hour)# check: which hour do most commits happen at (UTC — GitHub doesn't tell us the user's time zone)

        # every hour 0-23 now falls into exactly one tag (before, 4 a.m. slipped through to "Regular Hour")
        if most_common_hour >= 22 or most_common_hour < 4:
            time_tag = "Night Owl"
        elif 4 <= most_common_hour <= 10:
            time_tag = "Early Bird"
        else:
            time_tag = "Regular Hour"

    print(time_tag)


if __name__ == "__main__":
    main()
