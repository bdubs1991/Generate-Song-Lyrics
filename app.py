from flask import Flask, render_template
import json
import random

prod_model = json.load(open(r"venv/prod_model_folder/prod_model.json"))
length = random.randint(1, 15)
start_word = random.choice(list(prod_model.keys()))


def next_word(model, entered_word):
    word = entered_word[0]
    prob_words = model[word]
    words = list(model[word].keys())
    prob_weights = list(model[word].values())
    next_word = random.choices(words, weights=prob_weights)
    return next_word


def generate_lyrics(model, initial_word, sentence_length):
    lyrics_list = []
    lyrics_list.append(initial_word)
    i = 0
    while i < sentence_length:
        word = next_word(model, [lyrics_list[-1]])
        lyrics_list.append(word[0])
        i += 1
    sentence = " ".join(lyrics_list)
    return sentence


lyrics = generate_lyrics(prod_model, start_word, length)

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def my_form():
    return render_template('index.html', lyrics=lyrics)

if __name__ == '__main__':
    app.run()
