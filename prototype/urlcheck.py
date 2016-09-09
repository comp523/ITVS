
import requests
import urllib2

KEYWORDS = (
    "tobacco",
    "vape",
    "cig"
)


def check_url(url, keywords=KEYWORDS):
    #page = requests.get(url)
    page = urllib2.urlopen(url).read()
    for keyword in keywords:
        if keyword in page:
            return True
    return False


