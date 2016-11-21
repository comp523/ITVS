

import os
from ranalyze import database, scrape

subs = []
for sub in database.get_subreddits():
  subs.append(sub["value"])
print(subs)
scrape(subs)
