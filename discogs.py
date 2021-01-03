# This code uses sample code from an example of how oauthflow works with discogs api
# The code can be found at https://github.com/jesseward/discogs-oauth-example/blob/master/discogs_example.py
# Thank you to Jesse Ward for this example
import json
import sys

from urllib import request
from urllib.parse import parse_qsl
from urllib.parse import urlparse

import oauth2 as oauth

class Discord:

    def __init__(self):
        self.consumer_key = 'JJCOegYnRLCLRejtcZbo'
        self.consumer_secret = 'UFlGrCViqSkoBNfRTGZyUfmpTGNbFbMM'

        self.request_token_url = 'https://api.discogs.com/oauth/request_token'
        self.authorize_url = 'https://www.discogs.com/oauth/authorize'
        self.access_token_url = 'https://api.discogs.com/oauth/access_token'

        self.user_agent = 'discogs_api_example/1.0'
        self.user_name = None
        self.oauth_token = None
        self.oauth_token_secret = None

    def get_token(self):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)

        resp, content = client.request(self.request_token_url, 'POST', headers={'User-Agent': self.user_agent})

        if resp['status'] != '200':
            sys.exit('Invalid response {0}.'.format(resp['status']))

        request_token = dict(parse_qsl(content.decode('utf-8')))

        print(f'Please browse to the following URL {self.authorize_url}?oauth_token={request_token["oauth_token"]}')

        while oauth_verifier is None:
            print()
            oauth_verifier = input('Verification code : ')

        # secret to the discogs access_token_url
        token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(self.access_token_url, 'POST', headers={'User-Agent': self.user_agent})

        access_token = dict(parse_qsl(content.decode('utf-8')))
        self.oauth_token = request_token['oauth_token']
        self.oauth_token_secret = request_token['oauth_token_secret']
        return True


# We're now able to fetch an image using the application consumer key and secret,
# along with the verified oauth token and oauth token for this user.
    def get_collection(self, oauth_token, oauth_token_secret):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
        client = oauth.Client(consumer, token)

        resp, content = client.request('https://api.discogs.com/oauth/identity', headers={'User-Agents': self.user_agent})
        user = json.loads(content.decode('utf-8'))

        # With an active auth token, we're able to reuse the client object and request
        # additional discogs authenticated endpoints, such as database search.
        username = user['username']
        resp, content = client.request(f'https://api.discogs.com/users/{username}/collection/folders',
                                        headers={'User-Agents': self.user_agent})

        if resp['status'] != '200':
            sys.exit('Invalid API response {0}.'.format(resp['status']))

        collection = json.loads(content.decode('utf-8'))
        return collection, username


    def select_collection_and_get_albums(self, collection, oauth_token, oauth_token_secret, username):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
        client = oauth.Client(consumer, token)
        users_collection = []
        i = 0
        for x in collection['folders']:
            print(i, x['name'], "count: " + str(x['count']))
            users_collection.append(x['id'])

        selection = input("please enter the index of which folder you would like to select: ")
        folder_id = users_collection[selection]

        resp, content = client.request(f'https://api.discogs.com/users/{username}/collection/folders/{folder_id}/releases',
                                       headers={'User-Agents': self.user_agent})

        if resp['status'] != '200':
            sys.exit('Invalid API response {0}.'.format(resp['status']))
