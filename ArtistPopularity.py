import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.request import urlopen
from dotenv import load_dotenv

from PIL import Image
import tkinter as tk

import datetime as dt
from matplotlib import pyplot
from matplotlib import dates as plotdates

load_dotenv()
client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")
spot = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

def search(keyword):
    search = spot.search(q=keyword, type="artist", limit=10)
    results = search['artists']['items']
#    lista = {i['id']:i['name'] for i in results}
    artist = results[0]
    return clean_artist(artist)

def clean_artist(inp):
    outp = {}
    image_url = inp['images'][0]['url']
    outp['img'] = Image.open(urlopen(image_url))
    outp['followers'] = inp['followers']['total']
    for key in inp:
        if key in ['id', 'genres', 'name', 'popularity']:
            outp[key] = inp[key]
    return outp

def clean_album(inp):
    outp = {}
    image_url = inp['images'][0]['url']
    outp['art'] = Image.open(urlopen(image_url))
    outp['artists'] = {artist['id']:artist['name'] for artist in inp['artists']}
    outp['date'] = dt.datetime.strptime(inp['release_date'],'%Y-%m-%d').date()
    for key in inp:
        if key in ['id', 'genres', 'label', 'name', 'popularity', 'total_tracks']:
            outp[key] = inp[key]
    return outp

def find_albums(artist):
    album_list = []
    for album in spot.artist_albums(artist['id'], limit=20)['items']:
        if 'US' in album['available_markets']:
            if album['name'] not in [entry['name'] for entry in album_list]:
                full_info = spot.album(album['id'])
                album_list.append(clean_album(full_info))
    return album_list

def graph_albums(albums):
    dates = []
    figure, axis = pyplot.subplots()
    for album in albums:
        dates.append(album['date'])
        axis.plot_date(album['date'], album['popularity'])
    axis.set_xticks(dates)
    strdates = [d.strftime("%d/%m/%Y") for d in dates]
    axis.set_xticklabels(strdates, rotation="45")

    for i, date in enumerate(dates):
        axis.annotate(albums[i]['name'], (albums[i]['date'], albums[i]['popularity']))

    pyplot.show()

def graph_artist(artist_name):
    artist = search(keyword = artist_name)
    albums = find_albums(artist)
    graph_albums(albums)

def window():
    main = tk.Tk()
    main.title("Search")

    title = tk.Label(main, text='Search Artist')
    title.grid(row=0)

    entry = tk.Entry(main, textvariable = '')
    entry.grid(row=1)

    button = tk.Button(main, text = 'search', command = lambda: graph_artist(entry.get()))
    button.grid(row=2)

    main.mainloop()

window()




# related_artists = {artist['id']:artist['name'] for artist in spot.artist_related_artists(artist_id)['artists']}
# print(related_artists)
