import argparse
import logging


import spotipy
from spotipy.oauth2 import SpotifyOAuth
#import requests
#import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

secret_codes = json.load(open('secrets.json', 'r'))

spotify_client_id = secret_codes.get('spotify_client_id')
spotify_client_secret = secret_codes.get('spotify_client_secret')

client_credential_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
#sp = spotipy.Spotify(client_credentials_manager=client_credential_manager)

logger = logging.getLogger('examples.create_playlist')
logging.basicConfig(level='DEBUG')


def get_args():
    parser = argparse.ArgumentParser(description='Creates a playlist for user')
    parser.add_argument('-p', '--playlist', required=True,
                        help='Name of Playlist')
    parser.add_argument('-d', '--description', required=False, default='',
                        help='Description of Playlist')
    return parser.parse_args()


def main():
    args = get_args()
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(client_credentials_manager=client_credential_manager)
    user_id = sp.me()['id']
    print(user_id)
    # sp.user_playlist_create(user_id, args.playlist)


if __name__ == '__main__':
    main()