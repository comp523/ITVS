#!/usr/bin/env python
"""
Analysis tool to traverse a set of subreddits extracting post information including:
 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
"""
import datetime
import unittest
import ranalyze


class RanalyzeTest(unittest.TestCase):
    
    EXPECTED = (
        ranalyze.Post("https://www.reddit.com/r/itvs_testing/comments/541kdo/radical_place_to_discuss_vaping/", # permalink
             "http://vapingunderground.com/", # url
             1, # num_comments
             1, # upvotes
             0, # downvotes
             "Radical place to discuss vaping", # title
             "2016-09-22T18:17:38", # time_submitted
             "2016-09-23T14:14:31.459507" # time_retrieved is unused, but required
        ),
        ranalyze.Post("https://www.reddit.com/r/itvs_testing/comments/541k35/vaping_is_so_cool/", # permalink
             "https://www.reddit.com/r/itvs_testing/comments/541k35/vaping_is_so_cool/", # url
             1, # num_comments
             1, # upvotes
             0, # downvotes
             "Vaping is so cool", # title
             "2016-09-22T18:15:51", # time_submitted
             "2016-09-23T14:14:31.459507" # time_retrieved is unused, but required
        )
    )

    def test_fetch_data(self):
        end = datetime.datetime.strptime("2016-9-23", "%Y-%m-%d").date()
        start = end - datetime.timedelta(days=14)
        
        for expected, actual in zip(self.EXPECTED, ranalyze.fetch_data(["itvs_testing"], start, end)):
            print("Verifying \"{0}\"".format(expected.title))
            self.assertEqual(actual[1].permalink, expected.permalink)
            self.assertEqual(actual[1].url, expected.url)
            self.assertEqual(actual[1].num_comments, expected.num_comments)
            self.assertEqual(actual[1].upvotes, expected.upvotes)
            self.assertEqual(actual[1].downvotes, expected.downvotes)
            self.assertEqual(actual[1].title, expected.title)
            self.assertEqual(actual[1].time_submitted, expected.time_submitted)


if __name__ == '__main__':
    unittest.main()
