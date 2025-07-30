from nessvec.indexers import Index  # <1>

index = Index(num_vecs=100_000)  # <2>

index.get_nearest("Engineer").round(2)

index.get_nearest("Programmer").round(2)

index.get_nearest("Developer").round(2)

"Chief" + "Engineer"

"Chief" + " " + "Engineer"

chief = (index.data[index.vocab["Chief"]]
    + index.data[index.vocab["Engineer"]])

index.get_nearest(chief)

answer_vector = wv['woman'] + wv['Europe'] + wv['physics'] +
    wv['scientist']

answer_vector = wv['woman'] + wv['Europe'] + wv['physics'] +\
    wv['scientist'] - wv['male'] - 2 * wv['man']

answer_vector = wv['Louis_Pasteur'] - wv['germs'] + wv['physics']

wv['Marie_Curie'] - wv['science'] + wv['music']

from nessvec.examples.ch06.nessvectors import *  # <1>

nessvector('Marie_Curie').round(2)

import torchtext

dsets = torchtext.datasets.WikiText2()

num_texts = 10000

filepath = DATA_DIR / f'WikiText2-{num_texts}.txt'

with open(filepath, 'wt') as fout:
    fout.writelines(list(dsets[0])[:num_texts])

!tail -n 3 ~/nessvec-data/WikiText2-10000.txt

import datasets

dset = datasets.load_dataset('text', data_files=str(filepath))

dset

dset = dset.map(tokenize_row)

dset

vocab = list(set(
    [tok for row in dset['train']['tokens'] for tok in row]))

vocab[:4]

id2tok = dict(enumerate(vocab))

list(id2tok.items())[:4]

tok2id = {tok: i for (i, tok) in id2tok.items()}

list(tok2id.items())[:4]

def windowizer(row, wsize=WINDOW_WIDTH):

dset = dset.map(windowizer)

dset

def skip_grams(tokens, window_width=WINDOW_WIDTH):
   pairs = []
   for i, wd in enumerate(tokens):
       target = tok2id[wd]
       window = [
           i + j for j in
           range(-window_width, window_width + 1, 1)
           if (i + j >= 0)
           & (i + j < len(tokens))
           & (j != 0)
       ]

from torch.utils.data import Dataset

class Word2VecDataset(Dataset):
   def __init__(self, dataset, vocab_size, wsize=WINDOW_WIDTH):
       self.dataset = dataset
       self.vocab_size = vocab_size
       self.data = [i for s in dataset['moving_window'] for i in s]

   def __len__(self):
       return len(self.data)

   def __getitem__(self, idx):
       return self.data[idx]

model = Word2Vec()

model

import torch

if torch.cuda.is_available():
    device = torch.device('cuda')

else:
    device = torch.device('cpu')

device

model.to(device)

from tqdm import tqdm  # noqa

EPOCHS = 10

LEARNING_RATE = 5e-4

from nlpia.data.loaders import get_data

word_vectors = get_data('word2vec')

from gensim.models.keyedvectors import KeyedVectors

word_vectors = KeyedVectors.load_word2vec_format(\
    '/path/to/GoogleNews-vectors-negative300.bin.gz', binary=True)

from gensim.models.keyedvectors import KeyedVectors

from nlpia.loaders import get_data

word_vectors = get_data('w2v', limit=200000)  # <1>

word_vectors.most_similar(positive=['cooking', 'potatoes'], topn=5)

word_vectors.most_similar(positive=['germany', 'france'], topn=1)

word_vectors.doesnt_match("potatoes milk cake computer".split())

word_vectors.most_similar(positive=['king', 'woman'],
    negative=['man'], topn=2)

word_vectors.similarity('princess', 'queen')

word_vectors['phone']

token_list

from gensim.models.word2vec import Word2Vec

num_features = 300  # <1>

min_word_count = 3  # <2>

num_workers = 2  # <3>

window_size = 6  # <4>

subsampling = 1e-3  # <5>

model = Word2Vec(
    token_list,
    workers=num_workers,
    size=num_features,
    min_count=min_word_count,
    window=window_size,
    sample=subsampling)

model.init_sims(replace=True)

model_name = "my_domain_specific_word2vec_model"

model.save(model_name)

from gensim.models.word2vec import Word2Vec

model_name = "my_domain_specific_word2vec_model"

model = Word2Vec.load(model_name)

model.most_similar('radiology')

from nessvec.files import load_fasttext

df = load_fasttext()  # <1>

df.head().round(2)

df.loc['prosocial']  # <2>

from nessvec.indexers import Index

index = Index()  # <1>

vecs = index.vecs

vecs.shape

import pandas as pd

vocab = pd.Series(wv.vocab)

vocab.iloc[1000000:100006]

wv['Illini']

import numpy as np

np.linalg.norm(wv['Illinois'] - wv['Illini'])  # <1>

cos_similarity = np.dot(wv['Illinois'], wv['Illini']) / (
    np.linalg.norm(wv['Illinois']) *\
    np.linalg.norm(wv['Illini']))  # <2>

cos_similarity

1 - cos_similarity # <3>

from nlpia.data.loaders import get_data

cities = get_data('cities')

cities.head(1).T

us = cities[(cities.country_code == 'US') &\
    (cities.admin1_code.notnull())].copy()

states = pd.read_csv(\
    'http://www.fonz.net/blog/wp-content/uploads/2008/04/states.csv')

states = dict(zip(states.Abbreviation, states.State))

us['city'] = us.name.copy()

us['st'] = us.admin1_code.copy()

us['state'] = us.st.map(states)

us[us.columns[-3:]].head()

vocab = pd.np.concatenate([us.city, us.st, us.state])

vocab = np.array([word for word in vocab if word in wv.wv])

vocab[:10]

city_plus_state = []

for c, state, st in zip(us.city, us.state, us.st):
    if c not in vocab:
        continue
    row = []
    if state in vocab:
        row.extend(wv[c] + wv[state])
    else:
        row.extend(wv[c] + wv[st])
    city_plus_state.append(row)

us_300D = pd.DataFrame(city_plus_state)

word_model.distance('man', 'nurse')

word_model.distance('woman', 'nurse')

from sklearn.decomposition import PCA

pca = PCA(n_components=2)  # <1>

us_300D = get_data('cities_us_wordvectors')

us_2D = pca.fit_transform(us_300D.iloc[:, :300])  # <2>

import seaborn

from matplotlib import pyplot as plt

from nlpia.plots import offline_plotly_scatter_bubble

df = get_data('cities_us_wordvectors_pca2_meta')

html = offline_plotly_scatter_bubble(
    df.sort_values('population', ascending=False)[:350].copy()\
        .sort_values('population'),
    filename='plotly_scatter_bubble.html',
    x='x', y='y',
    size_col='population', text_col='name', category_col='timezone',
    xscale=None, yscale=None,  # 'log' or None
    layout={}, marker={'sizeref': 3000})

import requests

repo = 'https://gitlab.com/tangibleai/nlpia2/-/raw/main'

name = 'Chapter-06_Reasoning-with-word-embeddings-word-vectors.adoc'

url = f'{repo}/src/nlpia2/data/{name}'

adoc_text = requests.get(url)

from pathlib import Path

path = Path.cwd() / name

with path.open('w') as fout:
    fout.write(adoc_text)

import subprocess

subprocess.run(args=[   # <1>
    'asciidoc3', '-a', '-n', '-a', 'icons', path.name])

if os.path.exists(chapt6_html) and os.path.getsize(chapt6_html) > 0:
    chapter6_html = open(chapt6_html, 'r').read()
    bsoup = BeautifulSoup(chapter6_html, 'html.parser')
    text = bsoup.get_text()  # <1>

import spacy

nlp = spacy.load('en_core_web_md')

config = {'punct_chars': None}

nlp.add_pipe('sentencizer', config=config)

doc = nlp(text)

sentences = []

noun_phrases = []

for sent in doc.sents:
    sent_noun_chunks = list(sent.noun_chunks)
    if sent_noun_chunks:
        sentences.append(sent)
        noun_phrases.append(max(sent_noun_chunks))

sent_vecs = []

for sent in sentences:
   sent_vecs.append(sent.vector)

import numpy as np

vector = np.array([1, 2, 3, 4])  # <1>

np.sqrt(sum(vector**2)) 

np.linalg.norm(vector)  # <2>

import numpy as np

for i, sent_vec in enumerate(sent_vecs):
    sent_vecs[i] = sent_vec / np.linalg.norm(sent_vec)

np_array_sent_vecs_norm = np.array(sent_vecs)

similarity_matrix = np_array_sent_vecs_norm.dot(
    np_array_sent_vecs_norm.T)  # <1>

import re

import networkx as nx

similarity_matrix = np.triu(similarity_matrix, k=1)  # <1>

iterator = np.nditer(similarity_matrix, flags=['multi_index'],

node_labels = dict()

G = nx.Graph()

pattern = re.compile(
   r'[\w\s]*[\'\"]?[\w\s]+\-?[\w\s]*[\'\"]?[\w\s]*'
   )  # <2>

for edge in iterator:
    key = 0
    value = ''
    if edge > 0.95:  # <3>
        key = iterator.multi_index[0]
        value = str(noun_phrases[iterator.multi_index[0]])
        if pattern.fullmatch(value)

import matplotlib.pyplot as plt

plt.subplot(1, 1, 1)  # <1>

pos = nx.spring_layout(G, k=0.15, seed=42)  # <1>

nx.draw_networkx(G, pos=pos, with_labels=True, labels=node_labels,

plt.show()
