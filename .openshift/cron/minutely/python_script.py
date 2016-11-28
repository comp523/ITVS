

import os
from ranalyze import scrape
from ranalyze.scrape import get_subreddits

subs = []
for sub in get_subreddits():
  subs.append(sub["value"])
print(subs)
scrape(subs)
