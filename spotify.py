import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import json

def set_up():
    secret_codes = json.load(open('secrets.json', 'r'))

    spotify_client_id = secret_codes.get('spotify_client_id')
    spotify_client_secret = secret_codes.get('spotify_client_secret')

    client_credential_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credential_manager)
    return sp

def get_id_from_album_name(sp, album):
    results = sp.search(q='album:' + album, type='album')
    return results

def get_id_from_song_name(sp, song):
    results = sp.search(q='song:' + song, type='song')
    return results

def get_id_from_artist_name(sp, artist):
    results = sp.search(q='artist:' + artist, type='artist')
    return results

def check_id_is_correct(sp, id, name, id_type):
    # get the results from spottify
    if 'song' in id_type:
        results = sp.song(id)
    if 'album' in id_type:
        results = sp.album(id)
    if 'artist' in id_type:
        results = sp.artist(id)
    
    # check if results is the same as name
    if name in results:
        return True
    return False

def create_playlist(sp, playlist_name='Discogs Collection'):
    user_name = sp.current_user()
    playlist = sp.create_playlist(user_name, name=playlist_name)
    return playlist

def update_playlist(sp, playlist_id, ids_to_add):
    user_name = sp.currect_urser()
    for song in ids_to_add:
        sp.user_playist_add_tracts(user_name, playlist_id, song)
    return True
