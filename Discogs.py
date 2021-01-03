# This illustrates the call-flow required to complete an OAuth request
# against the discogs.com API. The script will download and save a single
# image from the discogs.com API as an example.
# See README.md for further documentation.
#
import json
import sys

from urllib import request
from urllib.parse import parse_qsl
from urllib.parse import urlparse

import oauth2 as oauth

consumer_key = 'JJCOegYnRLCLRejtcZbo'
consumer_secret = 'UFlGrCViqSkoBNfRTGZyUfmpTGNbFbMM'

request_token_url = 'https://api.discogs.com/oauth/request_token'
authorize_url = 'https://www.discogs.com/oauth/authorize'
access_token_url = 'https://api.discogs.com/oauth/access_token'

user_agent = 'discogs_api_example/1.0'


def get_token():
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    resp, content = client.request(request_token_url, 'POST', headers={'User-Agent': user_agent})

    if resp['status'] != '200':
        sys.exit('Invalid response {0}.'.format(resp['status']))

    request_token = dict(parse_qsl(content.decode('utf-8')))

    print(f'Please browse to the following URL {authorize_url}?oauth_token={request_token["oauth_token"]}')

    while oauth_verifier is None:
        print()
        oauth_verifier = input('Verification code : ')

    # secret to the discogs access_token_url
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, 'POST', headers={'User-Agent': user_agent})

    access_token = dict(parse_qsl(content.decode('utf-8')))

    return access_token["oauth_token"], access_token["oauth_token_secret"]


# We're now able to fetch an image using the application consumer key and secret,
# along with the verified oauth token and oauth token for this user.
def get_collection(oauth_token, oauth_token_secret):
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request('https://api.discogs.com/oauth/identity', headers={'User-Agents': user_agent})
    user = json.loads(content.decode('utf-8'))

    # With an active auth token, we're able to reuse the client object and request
    # additional discogs authenticated endpoints, such as database search.
    username = user['username']
    resp, content = client.request(f'https://api.discogs.com/users/{username}/collection/folders',
                               headers={'User-Agents': user_agent})

    if resp['status'] != '200':
        sys.exit('Invalid API response {0}.'.format(resp['status']))

    collection = json.loads(content.decode('utf-8'))
    return collection, username


def select_collection_and_get_albums(collection, oauth_token, oauth_token_secret, username):
    consumer = oauth.Consumer(consumer_key, consumer_secret)
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
                               headers={'User-Agents': user_agent})

    if resp['status'] != '200':
        sys.exit('Invalid API response {0}.'.format(resp['status']))


# resp, content = client.request('https://api.discogs.com/database/search?release_title=House+For+All&artist=Blunted+Dummies',
#         headers={'User-Agent': user_agent})
#
# if resp['status'] != '200':
#     sys.exit('Invalid API response {0}.'.format(resp['status']))
#
# releases = json.loads(content.decode('utf-8'))
# print('\n== Search results for release_title=House For All, Artist=Blunted Dummies ==')
# for release in releases['results']:
#     print(f'\n\t== discogs-id {release["id"]} ==')
#     print(f'\tTitle\t: {release.get("title", "Unknown")}')
#     print(f'\tYear\t: {release.get("year", "Unknown")}')
#     print(f'\tLabels\t: {", ".join(release.get("label", ["Unknown"]))}')
#     print(f'\tCat No\t: {release.get("catno", "Unknown")}')
#     print(f'\tFormats\t: {", ".join(release.get("format", ["Unknown"]))}')
#
# # In order to download release images, fetch the release data for id=40522
# # 40522 = http://www.discogs.com/Blunted-Dummies-House-For-All/release/40522
# resp, content = client.request('https://api.discogs.com/releases/40522',
#         headers={'User-Agent': user_agent})
#
# if resp['status'] != '200':
#     sys.exit('Unable to fetch release 40522')
#
# # load the JSON response content into a dictionary.
# release = json.loads(content.decode('utf-8'))
# # extract the first image uri.
# image = release['images'][0]['uri']
#
# # The authenticated URL is generated for you. There is no longer a need to
# # wrap the image download request in an OAuth signature.
# # build, send the HTTP GET request for the desired image.
# # DOCS: http://www.discogs.com/forum/thread/410594
# try:
#     request.urlretrieve(image, image.split('/')[-1])
# except Exception as e:
#     sys.exit(f'Unable to download image {image}, error {e}')
#
# print(' == API image request ==')
# print(f'    * response status      = {resp["status"]}')
# print(f'    * saving image to disk = {image.split("/")[-1]}')