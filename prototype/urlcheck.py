
"""
Checks if a given URL is an ITV
"""

import urllib.request as request

KEYWORDS = (
    "tobacco",
    "vape",
    "cig"
)


"""
documentation
"""
def check_url(url, keywords=KEYWORDS):
    # `in` operator only works with consistent data types, urlopen.read returns bytes
    page = str(request.urlopen(url).read())
    for keyword in keywords:
        if keyword in page:
            return True
    return False
