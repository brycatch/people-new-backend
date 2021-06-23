import lxml.html as html
import requests
import os
import base64

WIKI_BASE_URL = 'https://en.wikipedia.org/wiki/'

def parse_wiki_bio(artist: str) -> str:
    try:
        response = requests.get(f'{WIKI_BASE_URL}{artist.replace(" ", "_").title()}')
        if response.status_code == 200:
            famous = response.content.decode('utf-8')
            parsed = html.fromstring(famous)
            try:
                bio = str(parsed.xpath('normalize-space(//p[preceding-sibling::table[@class="infobox biography vcard"] and following-sibling::div[@class="toc"]])'))
                return bio
            except IndexError:
                return 
    except ValueError as ve:
        print(ve)


def query_artist(artist: str) -> dict:
    url = f'https://api.celebrityninjas.com/v1/search?name={artist.title()}'
    api_key = os.environ['apikey']
    headers = {'x-api-key': api_key}
    print(headers)
    resp = requests.get(url=url, headers=headers)
    if resp.status_code == 200 and resp.json() != []:
            return resp.json()[0]
    return {'message': 'The query did not return any results'}


def join_artist_with_bio(bio: str, artist: dict) -> dict:
    artist['bio'] = bio
    return artist

# Spotify API For music portion
def auth() -> str:
    client_id = os.environ['client_id_sp']
    client_secret = os.environ['client_secret_sp']
    # Check the testResponse Json for further reference
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}
    message = f'{client_id}:{client_secret}'

    # Base 64 encode
    messageBytes = message.encode('ascii')
    base64bytes = base64.b64encode(messageBytes)
    base64Message = base64bytes.decode('ascii')
    headers['Authorization'] = f'Basic {base64Message}'
    data['grant_type'] = "client_credentials"
    result = requests.post(url, headers=headers, data=data)
    token = result.json()['access_token']
    return token


BASE_SPOTIFY_URL = 'https://api.spotify.com/v1'


def set_spotify_header_request() -> dict:
    token = auth()
    return {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {token}'
    }


def get_album_details(albumId: str) -> dict:
    headers = set_spotify_header_request()
    params={'market': 'ES'}
    album = requests.get(url=f'{BASE_SPOTIFY_URL}/albums/{albumId}?market=ES', headers=headers)
    if album.status_code == 200:
        album_json = album.json()
        total_duration = 0
        for item in album_json['tracks']['items']:
            total_duration += item['duration_ms']

        response_object = {
            'Name': album_json['name'],
            'Total_tracks': album_json['total_tracks'],
            'Duration_in_minutes': (total_duration/1000)//60
        }
        return response_object


def get_artist_albums_ids(artistId: str) -> list:
    headers = set_spotify_header_request()
    albums = requests.get(url=f'{BASE_SPOTIFY_URL}/artists/{artistId}/albums?include_groups=album&market=ES&limit=50&offset=0', headers=headers)
    if albums.status_code == 200:
        albums_json = albums.json()
        albums_ids = []
        for album in albums_json['items']:
            albums_ids.append(album['id'])
        return albums_ids

#print(auth())
#print(get_album_details('5EIVoKtfgnSc0nPzJS6lzy'))
# Make this a function
# muse_albums = get_artist_albums_ids('12Chz98pHFMPJEknJQMWvI')
# obj = []
# for item in muse_albums:
#     album = get_album_details(item)
#     obj.append(album)
# print(obj)


def get_most_sad_song(tracklist: list):
    valences = []
    for item in tracklist:
        new_item = item.replace('spotify:track:', '')
        headers = set_spotify_header_request()
        response = requests.get(url=f'{BASE_SPOTIFY_URL}/audio-features/{new_item}', headers=headers)
        if response.status_code == 200:
            r = response.json()
            valences.append(r['valence'])
    print(f'valences {valences}')
    print(min(valences))
    
#print(get_most_sad_song_user(track_list))

        


# artist = 'Matthew Belamy'
# bio = parse_wiki_bio(artist)
# details = query_artist(artist)
# print(join_artist_with_bio(bio, details))