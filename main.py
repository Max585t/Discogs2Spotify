import discogs
import spotify

d_boi = discogs.Discord()
o_t, o_t_s = d_boi.get_token()
print(o_t, o_t_s)
collection, username = d_boi.get_collection()
d_boi.select_collection_and_get_albums(collection, username)