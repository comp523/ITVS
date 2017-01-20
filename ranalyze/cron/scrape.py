from ranalyze import scrape
from ranalyze.scrape import get_subreddits

print("starting scrape...")

# order subs by last_scrape (oldest first)
subs = [s['name'] for s in sorted(get_subreddits(), key=lambda s: s["last_scraped"] or 0)]

print("scraping", subs)

scrape(subs)

print("done scraping")
