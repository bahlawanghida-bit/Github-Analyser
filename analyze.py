import os
import pandas as pd
import json


username = input("enter the github username: ")
output_filename = os.path.join("data", f"{username}_github_data.json") #create a file name using the username of the account inside the file "data"
with open(output_filename, "r") as f: #read a file 
    output=json.load(f)

print(f"Data loaded from {output_filename}")

df= pd.DataFrame(output) # turn list of dictionary into tables for data each dict is a row, and each dict's keys become column names.
print(df)

language_totals = {}
# empty dict to hold running byte totals per language, across all repos

for repo in output:
    # loop through every repo dict in the loaded data
    for language_name, language_bytes in repo["languages"].items():
        # loop through each language in this repo, getting both its name and byte count
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
sorted_df = df.sort_values("commit_count", ascending = False)# sort all repos by commit_count, highest first
print(sorted_df[["name", "commit_count"]])# check: repos sorted by commit_count, highest first — only showing name and count for readability
most_active_repo = sorted_df.iloc[0]# grab the very first row of the sorted DataFrame — the repo with the highest commit_count
print(most_active_repo)# check: details of the single most active repo

all_commit_dates = []# empty list to hold every commit timestamp across all repos, flattened into one list

for repo in output:# loop through every repo dict
    all_commit_dates.extend(repo["commit_dates"]) # add all of this repo's commit dates into the combined flat list

print(len(all_commit_dates))# check: total number of commits across the whole account

commit_datetimes = pd.to_datetime(all_commit_dates) # convert the raw ISO date strings into real datetime objects pandas can analyze

print(commit_datetimes)# check: see the converted datetime values

commit_hours= commit_datetimes.hour# extract just the hour (0-23) from each commit's datetime
print(commit_hours)# check: see all the hours commits happened at


hour_counts= commit_hours.value_counts()# count how many commits happened during each hour, across the whole account
print(hour_counts)# check: commit frequency by hour of day


  #bahlawanghida-bit

  