

import os
from ranalyze import scrape

subs = []
with open(os.environ["$OPENSHIFT_DATA_DIR"]+"/config.txt", "wt") as config_file:
  for line in config_file:
    subs.append(line)
print subs
scrape.scrape(subs)
