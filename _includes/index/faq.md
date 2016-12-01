# Frequently asked questions

How do I search?

Searching is done in the Search tab by entering a list of space seperated keywords in keywords mode or by entering an expression in expression mode.

Expressions are of the format "word" and "other word" or not "third word"

What do the word frequency sliders do?

The sliders determine the coefficients x and y in the weight calculation used to rank words in the word cloud. The formula is: number_of_posts_with_word * x + number_of_times_word_was_used * y = weight

I deleted a subreddit from the settings. Why is it still in the search results?

Deleting a subreddit from the settings page only stops the automatic scraping of that subreddit. All data is retained when a subreddit is removed from the settings page. If you want to delete some data you will need to access the database directly.

I added a subreddit to the settings, why can't I find any results for it?

Subreddits are scraped automatically, but it will take some time for a subreddit to be initially scraped. The last 1000 posts on a subreddit are scraped after it is added to the settings page, and scraping this many posts can take some time. 