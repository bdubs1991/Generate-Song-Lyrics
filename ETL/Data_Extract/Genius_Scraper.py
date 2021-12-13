#!/usr/bin/env python
# coding: utf-8

#import libraries

import requests
import re
from bs4 import BeautifulSoup
import nltk
import numpy as np
import math
import pandas as pd
from datetime import date

def artist_song_page_lookup(artist_api,token,page):
    base_url = 'https://api.genius.com'
    artist_url = base_url + '{}/songs'.format(artist_api)
    headers = {'Authorization': 'Bearer ' + token}
    params = {'sort':'popularity','page': page} # the current page
    response = requests.get(artist_url, headers=headers,params=params).json()['response']['songs']
    return response

#looks up the artist into genius.com's API
def artist_lookup(artist_name,token):
    api_path = 'No Artist Found'
    headers = {'Authorization': 'Bearer ' + token}
    search_url = 'https://api.genius.com/search?q=' + artist_name
    response = requests.get(search_url, headers=headers).json()['response']['hits']
    for artist in response:
        if artist_name.lower() == artist['result']['primary_artist']['name'].lower():
            api_path = artist['result']['primary_artist']['api_path']
            break
    if api_path == 'No Artist Found':
        print('No Artist Found')
    return api_path


def artist_data(artist_list,token):
    artists_df = []
    for artist in artist_list:
        artist_api = artist_lookup(artist,token)
        if artist_api != 'No Artist Found':
            artist_df = song_df(artist_api,token)
            artists_df.append(artist_df)
    return artists_df
        

#pulls the Urls and song title out of the API's output
def song_details(response):
    urls = []
    songs = []
    artist = []
    api_paths = []
    #change this to be a dictionary
    for song in response:
        songs.append(song['title'])
        urls.append(song['url']) 
        artist.append(song['primary_artist']['name'])
        api_paths.append(song['api_path'])
    return urls,songs,artist,api_paths



#scrapes the lyrics from the website, using the given urls
def lyric_scraper(urls):
    lyrics = []
    for url in urls:
        page = requests.get(url)
        html = BeautifulSoup(page.text, 'html.parser')
        div = html.find('div', class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is not None:
            lyrics.append(lyrics_cleaner(div.get_text()))
        else:
            lyrics.append(' Lyrics for this song have yet to be released.  Please check back once the song has been released')    
    return lyrics


#pulls the verse labels out of the lyrics
def lyrics_cleaner(song):
    verse_labels_removed = re.sub("[\(\[].*?[\)\]]", "", song)
    hyperlinks_removed = re.sub(r"[0-9]*EmbedShare URLCopyEmbedCopy",'',verse_labels_removed)
    hyperlinks_removed = re.sub(r"EmbedShare URLCopyEmbedCopy",'',hyperlinks_removed)
    cleaned_song= re.sub( r"([A-Z])", r" \1",hyperlinks_removed)
    return cleaned_song


def get_all_artist_songs(artist_api,token):
    current_page = 1
    next_page = True
    songs = []
    while next_page is True:
        page_songs = (artist_song_page_lookup(artist_api,token,current_page))
        unique_songs = remastered_song_remover(page_songs,artist_api)
        songs.extend(unique_songs)
        current_page += 1
        if len(page_songs) == 0:
            next_page = False
    return songs

def get_song_info(api_paths,token):
    albums = []
    release_dates = []
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + token}
    for song in api_paths:
        response = requests.get(base_url + song, headers=headers)
        json = response.json()
        release_date = json['response']['song']['release_date']
        album = json['response']['song']['album']
        if release_date != None:
            release_dates.append(release_date)
        else:
            release_dates.append('None')
        if album != None:
            albums.append(album['name'])
        else:
            albums.append('None')
    return albums, release_dates,


def song_df(artist_api,token):
    labels = {0:'song',1:'artist',2:'lyrics',3:'url',4:'album',5:'release_date'}
    response = get_all_artist_songs(artist_api,token)
    urls,songs,artist,api_paths = song_details(response)
    lyrics = lyric_scraper(urls)
    albums,release_dates = get_song_info(api_paths,token)
    song_df = pd.DataFrame(zip(songs,artist,lyrics,urls,albums,release_dates))
    song_df = song_df.rename(columns = labels)
    song_df = blank_song_remover(song_df).reset_index(drop=True)
    return song_df

def remastered_song_remover(page_songs, artist_api):
    duplicate_flags = ['remix','sound track', 'live','music-video','version', 'grammys', 'mix', 'edit', 'vma', 'acoustic', 'demo', 'statement', 'radio', 'session', 'awards', 'extended', 'setlist']
    songs_with_lyrics = [song for song in page_songs if song['url'].endswith('-lyrics')]
    unique_songs = [song for song in songs_with_lyrics if not any(flag in song['url'] for flag in duplicate_flags)]
    unique_songs = [song for song in unique_songs if song['primary_artist']['api_path'] == artist_api]
    unique_songs = [song for song in unique_songs if song['lyrics_state'] == 'complete']
    return unique_songs

def blank_song_remover(song_df):
    today = date.today()
    blank_lyric_messages = ['TBA','SOON',' Lyrics for this song have yet to be released.  Please check back once the song has been released']
    song_df = song_df[~song_df.lyrics.isin(blank_lyric_messages)]
    song_df = song_df.dropna()
    song_df = song_df[song_df['album'] != 'None']
    song_df = song_df[song_df['release_date'] != 'None']
    return song_df

def song_remover(song_df,songs_to_remove):
    song_df = song_df[~song_df.lyrics.isin(songs_to_remove)]
    return song_df

#these will be moved over when I have some examples, but exist here for now as a reference. They were flagged with the duplicate detection functions
songs_to_remove_gaga = ['Yoü and I (Joe Biden Election Night Rally 2020)','Angel Down (Work Tape)','Boys Boys Boys (Manhattan Clique)']
gaga_clean_df = song_remover(gaga_df,songs_to_remove_gaga)
