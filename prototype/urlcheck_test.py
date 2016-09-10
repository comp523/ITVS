import unittest
import prototype.urlcheck as urlcheck


class TextUrlCheck(unittest.TestCase):
    
    def test_tobacco_url(self):
        self.assertTrue(urlcheck.check_url("https://www.e-cig.com/"))
        
    def test_non_tobacco_url(self):
        self.assertFalse(urlcheck.check_url("https://www.google.com/"))


if __name__ == '__main__':
    unittest.main()
