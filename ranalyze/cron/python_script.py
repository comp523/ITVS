

import os
from ranalyze import scrape
from ranalyze import imprt
from ranalyze.scrape import get_subreddits

print("Beginning scrape")
subs = []
for sub in get_subreddits():
  subs.append(sub["name"])
print("Scraping ",subs)
scrape(subs)
print("Done scraping")

print("Updating posts from last week")
update
print("Done updating")

print("Importing from import table")
imprt.import_from_table()
print("Done importing")
