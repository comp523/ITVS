from ranalyze import scrape, imprt, update_posts
from ranalyze.scrape import get_subreddits

print("Beginning scrape")

subs = [sub["name"] for sub in get_subreddits()]

print("Scraping ", subs)

scrape(subs)

print("Done scraping")

print("Updating posts from last week")

update_posts(7)

print("Done updating")

print("Importing from import table")

imprt.import_from_table()

print("Done importing")
