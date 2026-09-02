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







  #bahlawanghida-bit  

