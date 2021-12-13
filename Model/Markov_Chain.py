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
