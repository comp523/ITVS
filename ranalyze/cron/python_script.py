

import os
from ranalyze import scrape
from ranalyze.scrape import get_subreddits

print("Beginning scrape")
subs = []
for sub in get_subreddits():
  subs.append(sub["name"])
print("Scraping ",subs)
scrape(subs)
print("Done scraping")
