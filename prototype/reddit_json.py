"""
Contains the basic reddit webscraping.

Currently if run as main, if an argument is provided,
it searches the subreddit '/r/arg[0]' for the top
100 posts of all time and outputs all external urls
from the posts and comment sections of those posts
"""

from __future__ import print_function

__author__ = "Lukas O'Daniel"

import time
import json
import re
import requests
import sys


def json_request(session, url):
    """
    Performs a series of requests until it gets a 200
    Will cause the entire program to fail due to the assert here
    created to avoid many reddit sessions in the code

    :param session: reddit cookie session which helps with throtelling
    :param url: the url to send the request (including .json at the end)
    :return: the response for that url
    """
    time.sleep(2) # avoid throttling from reddit
    response = session.get(url)
    loop_counter = 0
    while response.status_code != 200 and loop_counter < 5:
        print("Error on response. Wating extra time to avoid further throtelling...")
        time.sleep(5)
        loop_counter += 1
        response = session.get(url)
    assert response.status_code == 200
    return response

def create_session():
    user_pass_dict = {
        'user': '___throw_a_way',
        'passwd': 'Password',
        'api_type': 'json'}

    # Setting up a session with username to have lower latency/throtelling
    print("Setting up reddit session...")
    session = requests.Session()
    session.headers.update({'User-Agent' : 'gathering tobacco data user:___throw_a_way'})
    session.post(r'http://www.reddit.com/api/login', data=user_pass_dict)
    print("Reddit session created!")

    return session


def get_links_top_all_time(subreddit, limit=200):
    """
    Retrieves JSON for the top 200 posts of all time in a given subreddit
    :param subreddit: subreddit name as it appears after /r/...
    :param limit: the number of posts intended to be returned
    :returns: a tuple of lists in the form (permalinks, external_links)

    TODO: consider a different manner to retrieve this data. This is done in one sweep
    """
    subreddit_url = ("http://www.reddit.com/r/"+
                     subreddit+
                     "/top/.json?sort=top&t=all&limit=100&after=")
    session = create_session()

    #j = json.loads(session_response.content) # TODO: figure out why included in example

    url_suffix = "" # included in the response is a string for
                    # how to get the correct next colleciton of results

    permalinks = []
    external_links = [] # this is the list that should be returned
    print("Retrieving all time top "+str(limit)+" posts for /r/"+subreddit+"...")
    while len(permalinks) < limit:
        request_url = subreddit_url + url_suffix
        response = json_request(session, request_url) # Make request to Reddit API
        
        json_response = json.loads(response.content)
        for post in json_response['data']['children']:
            if post['data']['is_self']: # post is not an external link
                permalinks.append(post['data']['url'])
            else:
                permalinks.append('https://www.reddit.com'+post['data']['permalink'])
                external_links.append(post['data']['url'])
        after = json_response['data']['after']
        print("Successfully retrieved "+str(len(permalinks))+"/"+str(limit)+" of top posts for /r/"+subreddit)
    return (permalinks, external_links)


def get_posted_links(permalinks):
    """
    Retrieves all links in the comments for a given post
    :param permalinks: a list of links to permalink (comment sections)
    :returns: a list of links found in the comments
    TODO: complete this method
    """
    print("Beginning permalink scraping...")
    session = create_session()

    def traverse_comment_tree(root, permalink):
        url_acc = []
        if 'data' in root and 'children' in root['data']:
            for child in root['data']['children']:
                if 'data' in child and 'body' in child['data']:
                    url_acc.extend(
                        re.findall(
                            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                            child['data']['body']
                            ) 
                        )
                traverse_comment_tree_subroutine(child, url_acc, permalink)
        return url_acc

    def traverse_comment_tree_subroutine(root, url_acc, permalink):
        if ('data' in root and
        'replies' in root['data'] and
        'data' in root['data']['replies'] and
        'children' in root['data']['replies']['data']
       ):
            for child in root['data']['replies']['data']['children']:
                # TODO: this code wasn't functioning properly. In deeply nested comment trees,
                # another request must be made which complicates and hugely bottlenecks things
                # The following is the general idea, but I think misses some corner cases
                # Additionally this is difficult to test
                if 'kind' in child and child['kind'] == 'more':
                    response = json_request(session, permalink+child['data']['id']+".json")
                    json_response = json.loads(response.content)
                    url_acc.extend(traverse_comment_tree(json_response[1], permalink))
                if 'data' in child and 'body' in child['data']:
                    url_acc.extend(
                        re.findall(
                            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                            child['data']['body']
                            ) 
                        )
                traverse_comment_tree_subroutine(child, url_acc, permalink)
    all_urls = []
    for permalink in permalinks:
        request_url = permalink + ".json"
        response = json_request(session, permalink + ".json")

        json_response = json.loads(response.content)

        all_urls.extend(traverse_comment_tree(json_response[1], permalink))
    return all_urls



if __name__ == '__main__':
    my_subreddit = 'dankmemes'
    if len(sys.argv) > 1:
        my_subreddit = sys.argv[1]
    permalinks, external_links = get_links_top_all_time(subreddit=my_subreddit, limit=100)
    print(permalinks[:1])
    print(get_posted_links(permalinks[:2]))
