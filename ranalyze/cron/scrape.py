from ranalyze import scrape
from ranalyze.scrape import get_subreddits

print("starting scrape...")

subs = list(get_subreddits())

print("scraping", subs)

scrape(subs)

print("done scraping")
