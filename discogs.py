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
        # create oauth Consumer and Client objects using
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)

        # pass in your consumer key and secret to the token request URL. Discogs returns
        # an ouath_request_token as well as an oauth request_token secret.
        resp, content = client.request(self.request_token_url, 'POST', headers={'User-Agent': self.user_agent})

        # we terminate if the discogs api does not return an HTTP 200 OK. Something is
        # wrong.
        if resp['status'] != '200':
            sys.exit('Invalid response {0}.'.format(resp['status']))

        request_token = dict(parse_qsl(content.decode('utf-8')))

        print(' == Request Token == ')
        print(f'    * oauth_token        = {request_token["oauth_token"]}')
        print(f'    * oauth_token_secret = {request_token["oauth_token_secret"]}')
        print()

        # Authorize our newly received request_token against the discogs oauth endpoint.
        # Prompt your user to "accept" the terms of your application. The application
        # will act on behalf of their discogs.com account.
        # If the user accepts, discogs displays a key to the user that is used for
        # verification. The key is required in the 2nd phase of authentication.
        print(f'Please browse to the following URL {self.authorize_url}?oauth_token={request_token["oauth_token"]}')

        # Waiting for user input
        accepted = 'n'
        while accepted.lower() == 'n':
            print()
            accepted = input(
                f'Have you authorized me at {self.authorize_url}?oauth_token={request_token["oauth_token"]} [y/n] :')

        # request the verification token from the user.
        oauth_verifier = input('Verification code : ')

        # Generate objects that pass the verification key with the oauth token and oauth
        # secret to the discogs access_token_url
        token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(self.access_token_url, 'POST', headers={'User-Agent': self.user_agent})

        # if verification is successful, the discogs oauth API will return an access token
        # and access token secret. This is the final authentication phase. You should persist
        # the oauth_token and the oauth_token_secret to disk, database or some
        # other local store. All further requests to the discogs.com API that require authentication
        # and must be made with these access_tokens.
        access_token = dict(parse_qsl(content.decode('utf-8')))

        print(' == Access Token ==')
        print(f'    * oauth_token        = {access_token["oauth_token"]}')
        print(f'    * oauth_token_secret = {access_token["oauth_token_secret"]}')
        print(' Authentication complete. Future requests must be signed with the above tokens.')
        print()

        # We're now able to fetch an image using the application consumer key and secret,
        # along with the verified oauth token and oauth token for this user.

        self.oauth_token = access_token['oauth_token']
        self.oauth_token_secret = access_token['oauth_token_secret']
        return request_token['oauth_token'], request_token['oauth_token_secret']


# We're now able to fetch an image using the application consumer key and secret,
# along with the verified oauth token and oauth token for this user.
    def get_collection(self):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        token = oauth.Token(key=self.oauth_token, secret=self.oauth_token_secret)
        client = oauth.Client(consumer, token)

        resp, content = client.request('https://api.discogs.com/oauth/identity', headers={'User-Agents': self.user_agent})
        print(content)
        user = json.loads(content.decode('utf-8'))
        print(user)
        # With an active auth token, we're able to reuse the client object and request
        # additional discogs authenticated endpoints, such as database search.
        username = user['username']
        resp, content = client.request(f'https://api.discogs.com/users/{username}/collection/folders',
                                        headers={'User-Agents': self.user_agent})

        if resp['status'] != '200':
            sys.exit('Invalid API response {0}.'.format(resp['status']))

        collection = json.loads(content.decode('utf-8'))
        return collection, username


    def select_collection_and_get_albums(self, collection, username):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        token = oauth.Token(key=self.oauth_token, secret=self.oauth_token_secret)
        client = oauth.Client(consumer, token)
        users_collection = []
        i = 0
        for x in collection['folders']:
            print(i, x['name'], "count: " + str(x['count']))
            users_collection.append(x['id'])
            i+=1

        selection = input("please enter the index of which folder you would like to select: ")
        folder_id = users_collection[int(selection)]

        resp, content = client.request(f'https://api.discogs.com/users/{username}/collection/folders/{folder_id}/releases',
                                       headers={'User-Agents': self.user_agent})

        if resp['status'] != '200':
            sys.exit('Invalid API response {0}.'.format(resp['status']))

        content = json.loads(content)

        releases = content.get("releases")

        num_pages = content.get("pagination").get("pages")
        if num_pages > 1:
            i = 1
            while i < num_pages:
                next_url = content.get("pagination").get("urls").get("next")
                print(next_url)
                resp, content = client.request(next_url,
                    headers={'User-Agents': self.user_agent})
                if resp['status'] == '200':
                    content = json.loads(content)
                    releases.append(content.get("releases"))
                else:
                    break
                i+=1

        print(releases)
