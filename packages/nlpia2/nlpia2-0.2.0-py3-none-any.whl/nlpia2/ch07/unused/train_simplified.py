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
from tqdm import tqdm

from model_simplified import CNNTextClassifier
from nlpia2.language_model import nlp


T0 = 1652404117  # number of seconds since 1970-01-01 as of May 12, 2022
MAX_SEED = 2**32 - 1
DATA_DIR = Path(__file__).parent / 'data'

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
log.setLevel(level=logging.INFO)


def tokenize_spacy(doc):
    return [tok.text for tok in nlp(doc) if tok.text.strip()]


def tokenize_re(doc):
    return [tok for tok in re.findall(r'\w+', doc)]


def cnn_output_size(desired_conv_output_size, embedding_size, kernel_lengths, strides):
    """ Calculate the number of encoding dimensions output from CNN layers

    Convolved_Features = ((embedding_size + (2 * padding) - dilation * (kernel - 1) - 1) / stride) + 1
    Pooled_Features = ((embedding_size + (2 * padding) - dilation * (kernel - 1) - 1) / stride) + 1

    source: https://pytorch.org/docs/stable/generated/torch.nn.Conv1d.html
    """
    out_pool_total = 0
    for kernel_len, stride in zip(kernel_lengths, strides):
        out_conv = ((embedding_size - 1 * (kernel_len - 1) - 1) // stride) + 1
        out_pool = ((out_conv - 1 * (kernel_len - 1) - 1) // stride) + 1
        out_pool_total += out_pool

    # Returns "flattened" vector (input for fully connected layer)
    return out_pool_total * desired_conv_output_size


def compute_output_seq_len(input_seq_len, kernel_lengths, stride):
    """ Calculate the number of encoding dimensions output from CNN layers

    From PyTorch docs:
      L_out = 1 + (L_in + 2 * padding - dilation * (kernel_size - 1) - 1) / stride
    But padding=0 and dilation=1, because we're only doing a 'valid' convolution.
    So:
      L_out = 1 + (L_in - (kernel_size - 1) - 1) // stride

    source: https://pytorch.org/docs/stable/generated/torch.nn.Conv1d.html
    """
    out_pool_total = 0
    for kernel_len in kernel_lengths:
        out_conv = (
            (input_seq_len - 1 * (kernel_len - 1) - 1) // stride) + 1
        out_pool = ((out_conv - 1 * (kernel_len - 1) - 1) // stride) + 1
        out_pool_total += out_pool

    # return the len of a "flattened" vector that is passed into a fully connected (Linear) layer
    return out_pool_total


class Parameters:

    def __init__(self):
        self.seq_len: int = 35
        self.filepath: Path = Path('disaster-tweets.csv')
        self.usecols: tuple = ('text', 'target')
        self.tokenizer: str = 'tokenize_re'

        self.vocab_size: int = 2000

        self.embedding_size: int = 64
        self.kernel_lengths: list = [2, 3, 4, 5]
        self.strides: list = [2, 2, 2, 2]
        self.conv_output_size: int = 32

        self.epochs: int = 10
        self.batch_size: int = 12
        self.learning_rate: float = 0.001
        self.test_size: float = 0.1

        self.dropout_portion: float = 0.2

        self.num_stopwords: int = 0
        self.case_sensitive: bool = True

        self.split_random_state: int = min(max(int((time.time() - T0)), 0), MAX_SEED)
        self.numpy_random_state: int = min(max(int((time.time() - T0 - self.split_random_state) * 1000), 0), MAX_SEED)
        self.torch_random_state: int = min(max(int((time.time() - T0 - self.split_random_state) * 1000000), 0), MAX_SEED)

        self.re_sub: str = r'[^A-Za-z0-9.?!]+'


HYPERPARAMS = Parameters()


def pad(sequence, pad_value=0, seq_len=HYPERPARAMS.seq_len):
    log.debug(f'BEFORE PADDING: {sequence}')
    padded = list(sequence)[:seq_len]
    padded = padded + [pad_value] * (seq_len - len(padded))
    log.debug(f'AFTER PADDING: {sequence}')
    return padded


def update_params(params=HYPERPARAMS, **kwargs):
    if kwargs.pop('win', False):
        kwargs['split_random_state'] = 850753
        kwargs['numpy_random_state'] = 704
        kwargs['torch_random_state'] = 704463
    for param_name, param_val in params.__dict__.items():
        log.info(f'DEFAULT: {param_name}: {param_val}')
        kwarg_val = kwargs.get(param_name)
        if kwarg_val is not None:
            if param_val is None:
                coerce_to_dest_type = int
            else:
                coerce_to_dest_type = type(param_val)
            if not isinstance(param_val, str) and isinstance(kwarg_val, str):
                kwarg_val = eval(kwarg_val)
            setattr(params, param_name, coerce_to_dest_type(kwarg_val))
            log.warning(f'NEW KWARGS: {param_name}: {getattr(params, param_name)} ({type(getattr(params, param_name))})')
    params.tokenizer_fun = globals().get(params.tokenizer, tokenize_re)
    if not params.filepath.is_file():
        params.filepath = Path(DATA_DIR) / params.filepath
    return params


def load_dataset(params, expand_glove_vocab=False, seq_len=35, vocab_size=2000, embedding_size=64, num_stopwords=0, **kwargs):
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
    params = update_params(params, **kwargs)
    split_random_state = params.split_random_state
    if split_random_state is None:
        split_random_state = kwargs.pop('split_random_state')
    split_random_state = int(split_random_state)

    # .Compute your vocabulary for GloVE embeddings

    import re
    from nessvec.files import load_vecs_df
    HOME_DATA_DIR = Path.home() / '.nlpia2-data'
    PAD_TOK = '<PAD>'

    df = pd.read_csv(HOME_DATA_DIR / 'disaster-tweets.csv')
    df = df[['text', 'target']]
    df['target'] = (df['target'] > 0).astype(int)
    counts = Counter(chain(*[
        re.findall(r'[\w]+', t.lower()) for t in df['text']]))    # <1>
    vocab = [tok for tok, count in counts.most_common(2000)[num_stopwords:]]  # <2>
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


class Pipeline(Parameters):

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
        log.info(kwargs)
        # params = update_params(params=self)
        # self.__dict__.update(params.__dict__)
        print(vars(self))

        dataset = load_dataset(
            expand_glove_vocab=False,
            seq_len=self.seq_len,
            **kwargs)
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

    pipeline_args, pipeline_kwargs = parse_argv(sys.argv)

    if len(pipeline_args):
        log.error(f'main.py does not accept positional args: {pipeline_args}')
    log.warning(f'kwargs: {pipeline_kwargs}')

    pipeline = Pipeline(**pipeline_kwargs)

    pipeline = pipeline.train()
    hyperparms = json.loads(pipeline.dump())

    # predictions = pipeline.predict()

    return dict(pipeline=pipeline, hyperparams=hyperparms)


if __name__ == '__main__':
    results = main()
    print("=" * 100)
    print("=========== HYPERPARMS =============")
    print(results['hyperparams'].keys())
    print("=" * 100)
