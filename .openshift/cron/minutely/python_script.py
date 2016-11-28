

import os
from ranalyze import scrape

subs = []
for sub in scrape.get_subreddits():
  subs.append(sub["value"])
print(subs)
scrape(subs)
