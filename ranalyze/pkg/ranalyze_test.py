"""
Analysis tool to traverse a set of subreddits extracting post information including:
 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
"""
import datetime
import sys
import unittest

from pkg import ranalyze
from .config import Config


class RanalyzeTest(unittest.TestCase):
    """
    Unit tests for the ranalyze module
    """
    EXPECTED_SUBREDDIT_DATA = {
        "541kdo":{ # id
         "permalink":"https://www.reddit.com/r/itvs_testing/comments/541kdo/radical_place_to_discuss_vaping/",
         "up_votes":1,
         #"up_ratio":1,
         "time_submitted":1474582658,
         #"time_updated":"2016-09-23T14:14:31.459507", 
         "posted_by":"dchiquit",
         "title":"Radical place to discuss vaping",
         "subreddit":"itvs_testing",
         "external_url":"http://vapingunderground.com/",
         "text_content":"",
         "gilded":False
        },
        "d7y3d8z":{ # id
         "root_id":"541kdo",
         "up_votes":1,
         "time_submitted":1474583379,
         "posted_by":"biddigs3",
         "text_content":"omg no way this place is the radicalest #vapenation",
         "parent_id":"t3_541kdo",
         "gilded":False,
        },
        "d82mfzb":{ # id
         "root_id":"541kdo",
         "up_votes":1,
         "time_submitted":1474898358,
         "posted_by":"dchiquit",
         "text_content":"omg we should totes discuss purchasing tobacco products there =D ",
         "parent_id":"t1_d7y3d8z",
         "gilded":False,
        },
         "541k35":{ # id
         "permalink":"https://www.reddit.com/r/itvs_testing/comments/541k35/vaping_is_so_cool/",
         "up_votes":1,
         #"up_ratio":1,
         "time_submitted":1474582551,
         #"time_updated":"2016-09-23T14:14:31.459507", 
         "posted_by":"dchiquit",
         "title":"Vaping is so cool",
         "subreddit":"itvs_testing",
         "external_url":"https://www.reddit.com/r/itvs_testing/comments/541k35/vaping_is_so_cool/",
         "text_content":"I love vaping",
         "gilded":False
        },
        "d7y2u6h":{ # id
         "root_id":"541k35",
         "up_votes":1,
         "time_submitted":1474582611,
         "posted_by":"dchiquit",
         "text_content":"omg me too! You should buy vaping products from [e-cig.com](https://www.e-cig.com/)!",
         "parent_id":"t3_541k35",
         "gilded":False,
        },
    }

    def test_fetch_data(self):
        """
        Tests the ranalyze.fetch_data() function against a private
        subreddit (r/itvs_testing) with known content
        """
        end = datetime.datetime.strptime("2016-9-23", "%Y-%m-%d").date()
        start = end - datetime.timedelta(days=14)
        for actual in ranalyze.fetch_data(["itvs_testing"], start, end):
            if not actual["id"] in self.EXPECTED_SUBREDDIT_DATA.keys():
                self.fail("No expected data for entry "+actual["id"])
            if "title" in actual.keys():
                print("Verifying post \"{0}\" ({1})...".format(actual["title"], actual["id"]))
            else:
                print("Verifying comment {0}->{1}".format(actual["root_id"], actual["id"]))
            expected = self.EXPECTED_SUBREDDIT_DATA[actual["id"]]
            for key in expected.keys():
                self.assertEqual(actual[key], expected[key])
    
    def test_config(self):
        """
        Tests config.py configuration loading
        """
        backup = sys.argv[:]
        
        sys.argv = [
            "ranalyze.py",
            
        ]
        
        print("Using arguments",sys.argv)
        
        Config.initialize()
        config = Config.get_config()
        
        sys.argv = backup

if __name__ == '__main__':
    unittest.main()