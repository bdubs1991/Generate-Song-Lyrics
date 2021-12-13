#!/usr/bin/env python
# coding: utf-8

def stopword_remover(song):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    lyrics = song.lower()
    word_list = [word for word in lyrics.split() if word not in stop_words]
    return word_list

def word_counter(lyrics):
    word_dict = {}
    unique_words = stopword_remover(lyrics)
    for word in unique_words:
        if word in word_dict.keys():
            word_dict[word] = word_dict[word]+1
        else:
            word_dict[word] = 1
    return word_dict

def cos_sim(vector1, vector2):
    
    # Get the common characters between the two character sets
    common_characters = vector1[1].intersection(vector2[1])
    # Sum of the product of each intersection character.
    product_summation = sum(vector1[0][character] * vector2[0]                  [character] for character in common_characters)
    # Gets the length of each vector from the word2vec output.
    length = vector1[2] * vector2[2]
    # Calculates cosine similarity and rounds the value to ndigits decimal places.
    if length == 0:
        # Set value to 0 if word is empty.
        similarity = 0
    else:
        similarity = product_summation/length
    return similarity

def word2vec(song_lyrics):
    counted_words = word_counter(song_lyrics)
    word_set = set(counted_words)
    length = math.sqrt(sum(c*c for c in counted_words.values()))
    return counted_words,word_set,length

def get_similarity(song_df,similarity_threshold):
    songs = song_df['song'].to_list()
    lyrics = song_df['lyrics'].to_list()
    urls = song_df['url'].to_list()
    results = []
    vector_list = [word2vec(song) for song in lyrics]
    for i in range(len(vector_list)):
        vector_1 = vector_list[i]
        for j in range(i+1,len(vector_list)):
            vector_2 = vector_list[j]
            similarity_score= cos_sim(vector_1,vector_2)
            if 1 >= similarity_score >= similarity_threshold:
                results.append([songs[i],urls[i], songs[j],urls[j], similarity_score,i,j])
            else:
                pass
            
    return results
