"""
Chimère:
Let be a source text T: 
We empty it of its nouns, its adjectives, and its verbs, however marking the place of each noun,
adjective and verb. The result is called a “mold”. It is also said that the text is prepared.

Let there be three target texts, S, A, V:
We extract the nouns from S, the adjectives from A, the verbs from V.
Using the prepared text T we replace the nouns deleted in T
by the nouns from S, in the order in which they were extracted;
same operation for the adjectives of A and the verbs of V. After having corrected,
as little as possible, to eliminate certain incompatibilities,
one ends up with an accommodated text, or chimera.
"""
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, TextField, SubmitField
from wtforms.widgets import TextArea
import nltk
import argparse
from typing import Dict, List
from flask import Flask
from flask import render_template
from flask import request
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
nltk.download('averaged_perceptron_tagger')

class ChimeraForm(FlaskForm):
    source_text = StringField('Source text:',[
        DataRequired()], widget=TextArea())
    noun_text = TextField('Nouns text:',[
        DataRequired()], widget=TextArea())
    verb_text = TextField('Verbs text:',[
        DataRequired()], widget=TextArea())
    adjective_text = TextField('Adjectives text:',[
        DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')

@app.route('/', methods=('GET', 'POST'))
def index():
    form = ChimeraForm()
    chimera = ''
    if form.validate_on_submit():
        print("HELLO WORLD")
        print(form.data)
        chimera = generate_chimera(
            source_text=form.data['source_text'],
            noun_text=form.data['noun_text'],
            verb_text=form.data['verb_text'],
            adjective_text=form.data['noun_text'],
        )
    return render_template('index.html', result=chimera, form=form)

def extract_noun_list(s: str) -> List[str]:
    tokenized_text = nltk.word_tokenize(s)
    tagged_text = nltk.pos_tag(tokenized_text)
    noun_list = []
    for i, tag in enumerate(tagged_text):
        if tag[0] in ['\n', 'o\'er', '”']:
            continue
        if tag[1] == 'NN':
            noun_list.append(tag[0])
    return noun_list

def extract_verb_map(s: str) -> Dict[str, List[str]]:
    tokenized_text = nltk.word_tokenize(s)
    tagged_text = nltk.pos_tag(tokenized_text)
    verb_map = {'VBD': [], 'VB': [], 'VBP': [], 'VBN': [], 'VBG': [], 'VBZ': []}
    for i, tag in enumerate(tagged_text):
        if tag[1] == 'VB':
            verb_map['VB'].append(tag[0])
        elif tag[1] == 'VBD':
            verb_map['VBD'].append(tag[0])
        elif tag[1] == 'VBP':
            verb_map['VBP'].append(tag[0])
        elif tag[1] == 'VBN':
            verb_map['VBN'].append(tag[0])
        elif tag[1] == 'VBG':
            verb_map['VBG'].append(tag[0])
        elif tag[1] == 'VBZ':
            verb_map['VBZ'].append(tag[0])
    return verb_map

def extract_adj_map(s: str) -> Dict[str, List[str]]:
    tokenized_text = nltk.word_tokenize(s)
    tagged_text = nltk.pos_tag(tokenized_text)
    adj_map = {'JJ': [], 'JJR': [], 'JJS': []}
    for i, tag in enumerate(tagged_text):
        if tag[1] == 'JJ':
            adj_map['JJ'].append(tag[0])
        elif tag[1] == 'JJR':
            adj_map['JJR'].append(tag[0])
        elif tag[1] == 'JJS':
            adj_map['JJS'].append(tag[0])
    return adj_map

def generate_chimera(source_text, noun_text, verb_text, adjective_text) -> str:
    noun_list = extract_noun_list(noun_text)
    verb_map = extract_verb_map(verb_text)
    adj_map = extract_adj_map(adjective_text)

    words = source_text.split(' ')
    print(f'Text file: {words}\n')
    text = nltk.Text(words)
    tokenized_text = nltk.word_tokenize(' '.join(words))

    tagged_text = nltk.pos_tag(words)
    print(f'tagged_text: {tagged_text}\n')

    new_text = ''
    noun_list_index = 0
    index_map = {
        'VB': 0,
        'VBD': 0,
        'VBP': 0,
        'VBN': 0,
        'VBZ': 0,
        'VBG': 0,
        'JJ': 0,
        'JJR': 0,
        'JJS': 0,
    }
    print(f'VERB LIST: {verb_map}')
    print(f'NOUN LIST: {noun_list}')
    print(f'ADJ LIST: {adj_map}')
    for i, tag in enumerate(tagged_text):
        if not(all('a' <= char <= 'z' for char in tag[0].lower())):
            # Non alphabetic character.
            new_text += tag[0]
        elif tag[0] in ['is', 'was', 'are', 'were']:
            # Non alphabetic character.
            new_text += tag[0]
        elif tag[1] == 'NN':
            if noun_list_index < len(noun_list):
                new_text += noun_list[noun_list_index]
                print(f'Replacing noun {tag[0]} with {noun_list[noun_list_index]}')
                noun_list_index += 1
            else:
                new_text += tag[0]
        elif tag[1] in ['VB', 'VBD', 'VBP', 'VBN', 'VBG', 'VBZ']:
            verb_list_len = len(verb_map[tag[1]])
            if index_map[tag[1]] < verb_list_len:
                verb_list = verb_map[tag[1]]
                print(f'Replacing verb {tag[0]} with {verb_list[index_map[tag[1]]]}')
                new_text += verb_list[index_map[tag[1]]]
                new_i = index_map[tag[1]]
                new_i += 1
                index_map[tag[1]] = new_i
            else:
                new_text += tag[0]
        elif tag[1] in ['JJ', 'JJR', 'JJS']:
            adj_list_len = len(adj_map[tag[1]])
            if index_map[tag[1]] < adj_list_len:
                adj_list = adj_map[tag[1]]
                new_text += adj_list[index_map[tag[1]]]
                new_i = index_map[tag[1]]
                new_i += 1
                index_map[tag[1]] = new_i
            else:
                new_text += tag[0]
        else:
            new_text += tag[0]
        new_text += ' '
    orig = ' '.join(words)
    print(f'Original file: \n {orig}')
    print(f'Tagged file: \n {tagged_text}')
    print(f'Combined file: \n {new_text}')
    return new_text

if __name__ == '__main__':
    app.run()
