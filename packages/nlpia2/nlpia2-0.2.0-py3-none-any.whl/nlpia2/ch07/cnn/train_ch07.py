""" Model params hard coded
FIXME: Verify predict and compute_accuracy() functions by comparing to older versions in git

$ python main.py
Epoch: 1, loss: 0.71129, Train accuracy: 0.56970, Test accuracy: 0.64698
...
Epoch: 10, loss: 0.38202, Train accuracy: 0.80324, Test accuracy: 0.75984
"""
import time
from collections import Counter
import json
from itertools import chain
import logging
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from tqdm import tqdm  # noqa

from model_ch07 import CNNTextClassifier
# from model_ch07 import calc_conv_out_seq_len  # noqa


T0 = 1652404117  # number of seconds since 1970-01-01 as of May 12, 2022
MAX_SEED = 2**32 - 1
DATA_DIR = Path(__file__).parent / 'data'

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
log.setLevel(level=logging.INFO)


def tokenize_re(doc):
    return [tok for tok in re.findall(r'\w+', doc)]


hyperparams_old = dict(
    expand_glove_vocab=False,
    seq_len=35,
    vocab_size=3000,
    embedding_size=50,
    num_stopwords=0,
    kernel_lengths=[2],
    strides=[1],
    batch_size=10,
    learning_rate=0.01,
    num_epochs=10,
)

# experiments/disaster_tweets_cnn_pipeline_24363.json  # May 29 16:12
hyperparams = {
    "expand_glove_vocab": False,
    "num_epochs": 10,
    "seq_len": 32,
    "usecols": ["text", "target"],
    "tokenizer": "tokenize_re",
    "embeddings": [2000, 64],
    "kernel_lengths": [2, 3, 4, 5],
    "strides": [2, 2, 2, 2],
    "conv_output_size": 32,
    "in_channels": 32,
    "planes": 1,
    "out_channels": 32,
    "groups": 1,
    "epochs": 10,
    "batch_size": 12,
    "learning_rate": 0.001,
    "test_size": 0.1,
    "dropout_portion": 0.2,
    "num_stopwords": 0,
    "case_sensitive": True,
    "split_random_state": 1460940,
    "numpy_random_state": 433,
    "torch_random_state": 433994,
    "re_sub": "[^A-Za-z0-9.?!]+",
    "vocab_size": 2000,
    "embedding_size": 64,
    #    "learning_curve": [],
    "loss": 0.11444409191608429,
    "train_accuracy": 0.8727193110494819,
    "test_accuracy": 0.7900262467191601,
}


def pad(sequence, pad_value=0, seq_len=hyperparams['seq_len']):
    log.debug(f'BEFORE PADDING: {sequence}')
    padded = list(sequence)[:seq_len]
    padded = padded + [pad_value] * (seq_len - len(padded))
    log.debug(f'AFTER PADDING: {sequence}')
    return padded


def load_dataset(
    expand_glove_vocab=hyperparams['expand_glove_vocab'],
    seq_len=hyperparams['seq_len'],
    vocab_size=hyperparams['vocab_size'],
    embedding_size=hyperparams['embedding_size'],
    num_stopwords=hyperparams['num_stopwords'],
    **kwargs,
):
    """ load and preprocess csv file: return [(token id sequences, label)...]

    1. Simplified: load the CSV
    2. Configurable: case folding
    3. Configurable: remove non-letters (nonalpha):
    4. Configurable: tokenize with regex or spacy
    5. Configurable: remove stopwords (frequent words)
    6. Configurable: filter infrequent words
    7. Simplified: compute reverse index
    8. Simplified: transform token sequences to integer id sequences
    9. Simplified: pad token id sequences
    10. Simplified: train_test_split
    """

    import re
    from nessvec.files import load_vecs_df
    HOME_DATA_DIR = Path.home() / '.nlpia2-data'
    PAD_TOK = '<PAD>'

    retval = {}
    df = pd.read_csv(HOME_DATA_DIR / 'disaster-tweets.csv')
    df = df[['text', 'target']]
    df['target'] = (df['target'] > 0).astype(int)
    counts = Counter(chain(*[
        re.findall(r'[\w]+', t.lower()) for t in df['text']]))    # <1>
    vocab = [tok for tok, count in counts.most_common(vocab_size + num_stopwords)[num_stopwords:]]  # <2>
    if PAD_TOK not in vocab:
        vocab = [PAD_TOK] + list(vocab)

    glove = load_vecs_df(HOME_DATA_DIR / 'glove.6B.50d.txt')
    num_glove_vecs, embed_dims = glove.shape
    new_embeddings = pd.DataFrame([pd.Series([0] * embed_dims, name=PAD_TOK)])
    glove = pd.concat([new_embeddings, glove])
    print(f'glove.shape {glove.shape}')
    print(glove)

    expand_glove_vocab = False
    if expand_glove_vocab:
        new_vocab = [tok for tok in vocab if tok not in new_embeddings.index]   # <3>
        vocab.extend(new_vocab)
        embed = []
        for tok in vocab:                                              # <4>
            if tok in glove.index:
                embed.append(glove.loc[tok])
            else:
                embed.append(np.zeros(embed_dims))
    else:
        vocab = [tok for tok in vocab if tok in glove.index]
        print(f'len(vocab) {len(vocab)}')
        embed = glove.loc[vocab].values
    embed = np.array(embed)
    print(f'glove.shape {glove.shape}')
    print(f'embed.shape {embed.shape}')
    embed = torch.Tensor(np.array(embed))
    print(f'embed.size() {embed.size()}')

    print(df)
    print(f'embed.size(): {embed.size()}')
    print(f'pd.Series(vocab):\n{pd.Series(vocab)}')

    # <1> tokenizing, case folding, and occurrence counting
    # <2> ignore the 3 most frequent tokens ("t", "co", "http")
    # <3> find
    # <3> skip unknown embeddings; alternatively create zero vectors
    # <4> ensure your embedding matrix is in the same order as your vocab

    # 7. compute reverse index
    tok2id = dict(zip(vocab, range(len(vocab))))

    # 8. Simplified: transform token sequences to integer id sequences
    id_sequences = [[i for i in map(tok2id.get, seq) if i is not None] for seq in df.text]

    # 9. Simplified: pad token id sequences
    padded_sequences = []
    for seq in id_sequences:
        padded_sequences.append(pad(seq, seq_len=35, pad_value=vocab.index(PAD_TOK)))
    padded_sequences = torch.IntTensor(padded_sequences)

    # 10. Configurable sampling for testset (test_size samples)
    retval = dict(zip(
        'x_train x_test y_train y_test'.split(),
        train_test_split(
            padded_sequences,
            list(df['target']),
            test_size=.1)))
    retval['vocab'] = vocab
    retval['tok2id'] = tok2id
    retval['embed'] = embed
    return retval


class DatasetMapper(Dataset):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


def calculate_accuracy(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    true_positives = 0
    true_negatives = 0
    for true, pred in zip(y_true, y_pred):
        if (pred >= 0.5) and (true == 1):
            true_positives += 1
        elif (pred < 0.5) and (true == 0):
            true_negatives += 1
        else:
            pass
    # Return accuracy
    return (true_positives + true_negatives) / len(y_true)


class Pipeline:

    def __init__(self, **kwargs):
        """
        win=True will set winning random seeds:
            "split_random_state": 850753,
            "numpy_random_state": 704,
            "torch_random_state": 704463,
            or
            python train.py --split_random_state=850753 --numpy_random_state=704 --torch_random_state=704463
        """
        super().__init__()
        self.__dict__.update(kwargs)
        print(vars(self))

        dataset = load_dataset(**kwargs)
        self.x_train = dataset['x_train']
        self.y_train = dataset['y_train']
        self.x_test = dataset['x_test']
        self.y_test = dataset['y_test']
        self.model = CNNTextClassifier(
            seq_len=self.seq_len,
            kernel_lengths=self.kernel_lengths,
            embeddings=tuple(dataset['embed'].size()))

    def train(self, X=None, y=None):

        self.trainset_mapper = DatasetMapper(self.x_train, self.y_train)
        self.testset_mapper = DatasetMapper(self.x_test, self.y_test)

        self.loader_train = DataLoader(self.trainset_mapper, batch_size=self.batch_size)
        self.loader_test = DataLoader(self.testset_mapper, batch_size=self.batch_size)

        optimizer = optim.RMSprop(self.model.parameters(), lr=self.learning_rate)

        self.learning_curve = []
        for epoch in range(self.num_epochs):
            self.model.train()
            predictions = []
            for x_batch, y_batch in self.loader_train:
                y_batch = y_batch.type(torch.FloatTensor)
                y_pred = self.model(x_batch)
                loss = F.binary_cross_entropy(y_pred, y_batch)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Save predictions
                predictions += list(y_pred.detach().numpy())

            test_predictions = self.predict()
            self.loss = loss.item()
            self.train_accuracy = calculate_accuracy(self.y_train, predictions)
            self.test_accuracy = calculate_accuracy(self.y_test, test_predictions)
            self.learning_curve += [[self.loss, self.train_accuracy, self.test_accuracy]]
            print(
                "Epoch: %d, loss: %.5f, Train accuracy: %.5f, Test accuracy: %.5f"
                % (epoch + 1, self.loss, self.train_accuracy, self.test_accuracy)
            )
        return self

    def predict(self, X=None):

        self.model.eval()  # evaluation mode
        predictions = []

        if X is not None:
            X_batches = zip([X], [[None] * len(X)])
        else:
            X_batches = list(zip(*self.loader_test))[0]
            y_batches = list(zip(*self.loader_test))[1]
        with torch.no_grad():
            for x_batch, y_batch in zip(X_batches, y_batches):
                y_pred = self.model(x_batch).detach().numpy()
                predictions += list(y_pred)
        return predictions

    def score(self, X, y):
        y_pred = self.predict(X)
        return np.mean((y_pred - y.detach.numpy())**2) ** .5

    def dump(self, filepath=None, indent=4):
        js = self.dumps(indent=indent)
        if filepath is None:
            t = int((time.time() - T0) / 60)
            filepath = f'disaster_tweets_cnn_pipeline_{t}.json'
        with open(filepath, 'w') as fout:
            fout.write(js)
        return js

    def dumps(self, indent=4):
        hashable_dict = {}
        for k, v in vars(self).items():
            if v is None or isinstance(v, (str, float, int, bool)):
                hashable_dict[k] = v
                continue
            if isinstance(v, (tuple, np.ndarray)):
                v = list(v)
            if isinstance(v, torch.Tensor):
                v = list(v.detach().numpy())
            if isinstance(v, list):
                if isinstance(v[0], torch.Tensor):
                    v = [list(x.detach().numpy()) for x in v]
            try:
                hashable_dict[k] = json.loads(json.dumps(v))
            except TypeError:
                pass
        return json.dumps(hashable_dict, indent=indent)


def parse_argv(sys_argv=sys.argv):
    argv = list(reversed(sys_argv[1:]))

    pipeline_args = []
    pipeline_kwargs = {}  # dict(tokenizer='tokenize_re')
    while len(argv):
        a = argv.pop()
        if a.startswith('--'):
            if '=' in a:
                k, v = a.split('=')
                k = k.lstrip('-')
            else:
                k = a.lstrip('-')
                v = argv.pop()
            pipeline_kwargs[k] = v
        else:
            pipeline_args.append(a)

    return pipeline_args, pipeline_kwargs


def main():

    cli_args, cli_kwargs = parse_argv(sys.argv)
    if len(cli_args):
        log.error(f'main.py does not accept positional args: {cli_args}')
    log.warning(f'kwargs: {cli_kwargs}')

    hyperparams.update(cli_kwargs)
    pipeline = Pipeline(**hyperparams)

    pipeline = pipeline.train()
    hyperparms = json.loads(pipeline.dump())

    # predictions = pipeline.predict()

    return dict(pipeline=pipeline, hyperparams=hyperparms)


if __name__ == '__main__':

    # results = main()
    cli_args, cli_kwargs = parse_argv(sys.argv)
    if len(cli_args):
        log.error(f'main.py does not accept positional args: {cli_args}')
    log.warning(f'kwargs: {cli_kwargs}')

    hyperparams.update(cli_kwargs)
    pipeline = Pipeline(**hyperparams)

    pipeline = pipeline.train()
    hyperparms = json.loads(pipeline.dump())

    # predictions = pipeline.predict()

    results = dict(pipeline=pipeline, hyperparams=hyperparms)
    print("=" * 100)
    print("=========== HYPERPARMS =============")
    print(results['hyperparams'].keys())
    print("=" * 100)
