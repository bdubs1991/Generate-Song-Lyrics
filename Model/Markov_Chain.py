#!/usr/bin/env python
# coding: utf-8
import sqlite3
import re
import random 


def generate_markov_chain(text_list):
    model = {}
    for text in text_list:
        clean_text = text_cleaner(text)
        model = conditional_word_counter(model,clean_text)
        model = word_probability(model)
    return model


def conditional_word_counter(model,text):
    for i in range(0, len(text)- 1):
        fragment = text[i]
        next_word = text[i+1]
        if fragment not in model:
            model[fragment] = {}
        if next_word not in model[fragment]:
            model[fragment][next_word] = 1
        else:
            model[fragment][next_word] += 1
    return model

def word_probability(model):
    for word in model.keys():
        word_sum = 0
        for next_word in model[word]:
            word_sum += model[word][next_word]
        for next_word in model[word]:
            model[word][next_word] /= word_sum
    return model


def text_cleaner(text):
    clean_text = text[0].lower()
    clean_text = re.sub('[!;:,<>.?@#$%^&*_~]', "", clean_text)
    clean_text = clean_text.split()
    return clean_text

def next_word(model,entered_word):
    word = entered_word[0]
    prob_words = model[word]
    words = list(model[word].keys())
    prob_weights = list(model[word].values())
    next_word = random.choices(words,weights=prob_weights)
    return next_word


def generate_lyrics(model,initial_word,sentence_length):
    lyrics_list = []
    lyrics_list.append(initial_word[0])
    i = 0
    while i < sentence_length:
        word = next_word(model,[lyrics_list[-1]])
        lyrics_list.append(word[0])
        i += 1
    sentence = " ".join(lyrics_list)
    return sentence
