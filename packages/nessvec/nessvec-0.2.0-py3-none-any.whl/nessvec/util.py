""" Utilities for loading word2vec and GloVe word embeddings for vector reasoning

The nessvec package is imported as a module within nlpia2: `nlpia2.nessvec.__init__.__all__` (`import *`)

# FIXME (2nd edition):
# `nessvec.load_vecs_df(uri)`
Should work with bz2, gz, csv, .txt absolute file paths, file names (in HOME_DATA_DIR) & remote URLs:
>>> glove = load_vecs_df(HOME_DATA_DIR / 'glove.6B.50d.txt')
>>> glove = load_vecs_df(HOME_DATA_DIR / 'glove.6B.50d.txt.bz2')
>>> url = 'https://gitlab.com/tangibleai/nlpia2/-'
>>> url += '/raw/main/src/nlpia2/data/glove.6B.50d.txt.bz2'
>>> glove = load_vecs_df(url)

# `nessvec.download`:
Download a URL to HOME_DATA_DIR and return local path. Should work like wget:
!wget https://gitlab.com/tangibleai/nlpia2/-/raw/main/src/nlpia2/data/glove.6B.50d.txt.bz2

# `nessvec.decompress`:
Decompress a binary zip/gz/bz2 file and convert bytes to strings:
>>> import bz2
>>> glovebytes = open('glove.6B.50d.txt.bz2', 'rb').read()
>>> glovetext = bz2.decompress(glovebytes).decode()
>>> with open('glove.6B.50d.txt', 'w') as fout:
...     fout.write(glovetext)
171337876

STANFORD_GLOVE_URLS = [
    'https://nlp.stanford.edu/data/glove.6B.zip',
    'https://nlp.stanford.edu/data/glove.42B.300d.zip',
    'https://nlp.stanford.edu/data/glove.840B.300d.zip',
    'https://nlp.stanford.edu/data/glove.twitter.27B.zip',
]

References:
  * https://nlp.stanford.edu/projects/glove/
  * https://nlp.stanford.edu/pubs/
  * https://nlp.stanford.edu/software/

"""
import re
import logging
import bz2  # Python 3.10
import gzip  # Python 3.10
from pathlib import Path
import urllib


import numpy as np
from tqdm import tqdm

from .constants import LARGE_FILES, DATA_DIR
from .re_patterns import cre_url


log = logging.getLogger(__name__)

# size: 6B | 42B | 84B | twitter.27B
GLOVE_ZIP_FILENAME_TEMPLATE = 'glove.{size}B.zip'
GLOVE_URL_TEMPLATE = 'http://nlp.stanford.edu/data/' + GLOVE_ZIP_FILENAME_TEMPLATE

# dim: 50 | 100 | 300 | 1000
GLOVE_FILENAME_TEMPLATE = 'glove.{size}B.{dim}d.txt'


STANFORD_GLOVE_URLS = [
    'https://nlp.stanford.edu/data/glove.6B.zip',
    'https://nlp.stanford.edu/data/glove.42B.300d.zip',
    'https://nlp.stanford.edu/data/glove.840B.300d.zip',
    'https://nlp.stanford.edu/data/glove.twitter.27B.zip',
]


ZIP_SUFFIXES = ('.gz', '.zip', '.bz2')


def find_file(path):
    """ Find a local file in DATA_DIR (DATA_DIR should be deprecated)

    >>> found_path = find_file(Path('constants') / 'LANG_ISO')
    >>> found_path.is_file()
    True
    >>> found_path.name
    'LANG_ISO.csv'
    """
    pathobj = Path(path)
    if pathobj.is_file():
        return pathobj
    if (DATA_DIR / pathobj).is_file():
        return DATA_DIR / pathobj
    for suf in ['.csv', '.txt', '.tsv']:
        p = pathobj.with_suffix(suf)
        if p.is_file():
            return p
        for zipsuf in ZIP_SUFFIXES:
            p = pathobj.with_suffix(suf + zipsuf)
            if p.is_file():
                return p
            p = DATA_DIR / p
            if p.is_file():
                return p
    # assert p and p.is_file(), f'File not found at {path} nor {p}'


def decompress_with(path, destpath=None, module=gzip):
    """ Open a compressed file, copy decodee bytes to new DATA_DIR / path.name, truncating the suffix """
    pathobj = find_file(path)
    with pathobj.open('rb') as fin:
        textbytes = fin.read()
    text = module.decompress(textbytes).decode()
    destpath = make_data_path(
        path=pathobj.with_suffix(''.join(pathobj.suffixes[:-1])))
    i = 1
    while destpath.is_file():
        # insert f'copy{i}' intermediate suffix before file type extension
        splitname = destpath.name.split('.')
        destpath = destpath.parent / '.'.join([splitname[0], f'copy{i}'] + splitname[1:])
        i += 1
    with destpath.open('w') as fout:
        fout.write(text)
    return destpath


def decrompress(path, module=None):
    """ Decrompress a zip, gz, bz2 file, convert bytes to str, return text file path

    >>> import bz2
    >>> glovebytes = open('glove.6B.50d.txt.bz2', 'rb').read()
    >>> glovetext = bz2.decompress(glovebytes).decode()
    >>> with open('glove.6B.50d.txt', 'w') as fout:
    ...     fout.write(glovetext)
    171337876
    """
    found_path = find_file(path)
    path = found_path
    suf = '.' + path.suffix.lower().split('.')[-1]
    assert suf in ZIP_SUFFIXES
    if suf == '.bz2':
        return decompress_with(path, module=bz2)
    if suf == '.gz':
        return decompress_with(path, module=gzip)
    raise ValueError(f'Unrecognized file extension (suffix): {suf} for found path {found_path} and path {path}.')


def make_data_path(path):
    path = Path(path).resolve()
    if len(path.parts) == 1:
        return DATA_DIR / path
    if not str(path).startswith(str(DATA_DIR)):
        path = DATA_DIR / path
    path.parent.mkdir(exist_ok=True, parents=True)
    return path


def glove_normalize(s):
    """ GloVe deletes whitespace instead of replacing with "_" (Word2Vec style)

    >>> glove_normalize('Los Angeles')
    'losangeles'
    """
    return re.sub(r'\s+', '', s).lower()


def word2vec_normalize(s):
    """ Word2Vec replaces whitespace with "_"

    >>> word2vec_normalize('Los Angeles')
    'Los_Angeles'
    """
    return re.sub(r'\s+', '_', s)


def normalize_vector(x):
    """ Convert to 1 - D np.array and divide vector by it's length(2 - norm)

    >>> normalize_vector([0, 1, 0])
    array([0., 1., 0.])
    >>> normalize_vector([1, 1, 0])
    array([0.707..., 0.707..., 0...])
    """
    # x = np.array(x).flatten()
    xnorm = np.linalg.norm(x) or 1
    xnorm = xnorm if np.isfinite(xnorm) else 1
    return x / xnorm


def cosine_similarity(a, b):
    """ 1 - cos(angle_between(a, b))

    >>> cosine_similarity([0, 1, 1], [0, 1, 0])  # 45 deg
    0.707...
    """
    a = normalize_vector(np.array(a).flatten())
    b = normalize_vector(np.array(b).flatten())
    return (a * b).sum()


def cosine_similarities(target, components):
    """ 1 - cos(angle_between(target, components)) where b is a matrix of vectors

    >>> cosine_similarities(target=[1, 2, 3], components=[[3, 4, 5], [-1, 3, -2]])
    array([0.98..., -0.07...])
    """
    # target = 'the'
    # components = 'one two the oregon'.split()
    # target = wv[target] if isinstance(target, str) else target
    # components = np.array([wv[c] for c in components]) if isinstance(components[0], str) else components
    target = normalize_vector(np.array(target).flatten())
    target = target.reshape((-1, 1))
    components = np.array(components)
    n_vecs, n_dims = components.shape
    if n_dims != target.shape[0] and target.shape[0] == n_vecs:
        components = components.T
        n_vecs, n_dims = components.shape()

    target = normalize_vector(target)
    # print(target.shape)
    norms = np.linalg.norm(components, axis=1).reshape(n_vecs, 1)
    # norms = norms.dot(np.ones((1, n_dims)))
    log.debug(norms)
    log.debug(components)
    components = components / norms
    # print(components.shape)
    return components.dot(target).flatten()


class DownloadProgressBar(tqdm):
    """ Utility class that adds tqdm progress bar to urllib.request.urlretrieve

    >>> filemeta = LARGE_FILES['floyd']
    >>> filename = Path(filemeta['path']).name
    >>> url = filemeta['url']
    >>> dest_path = str(Path(filemeta['path']))
    >>> with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as dpb:
    ...     urllib.request.urlretrieve(url, filename=dest_path, reporthook=dpb.update_to)
    ('...nessvec/data/corpora/wikipedia/floyd.pkl', < http.client.HTTPMessage... >)
    """

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def looks_like_url(url):
    """ Simplified check to see if the text appears to be a URL.

    Similar to `urlparse` but much more basic.

    Returns:
      True if the url str appears to be valid.
      False otherwise.

    >>> url = looks_like_url("totalgood.org")
    >>> bool(url)
    True
    """
    if not isinstance(url, str):
        return False
    if not isinstance(url, str) or len(url) >= 1024 or not cre_url.match(url):
        return False
    return True


def download_if_necessary(url_or_name, dest_path=None):
    """ Loads the file found in the local DATA_DIR or download it from the LARGE_FILES url

    >>> download_if_necessary('')
    """
    if not url_or_name:
        return None
    file_meta = LARGE_FILES.get(url_or_name) or {'url': url_or_name}
    log.debug(f'file_meta: {file_meta}')
    url = file_meta['url']
    if not dest_path and not looks_like_url(url):
        if Path(url).is_file():
            dest_path = url
        if Path(DATA_DIR, url).is_file():
            dest_path = url
    dest_path = dest_path or file_meta.get('path')
    # TODO: walk down from URL filename to match up with directories in DATA_DIR to build dest path
    if not dest_path:
        dest_path = file_meta.get('path', Path(DATA_DIR, file_meta.get('filename', Path(url).name)))
    filename = Path(dest_path).name
    if Path(dest_path).is_file():
        with urllib.request.urlopen(url) as file:
            cloud_file_size = file.info()['Content-Length']
        local_file_size = str(dest_path.stat().st_size)
        if cloud_file_size == local_file_size:
            return dest_path
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as dpb:
        try:
            urllib.request.urlretrieve(url, filename=dest_path, reporthook=dpb.update_to)
        except (urllib.error.HTTPError, ValueError):
            log.error(f'Unable to download file from "{url}" to "{dest_path}" using file_meta: {file_meta}.')
            return None
    return dest_path


def filter_vocab(df, vocab):
    # filter out the rows with these words
    # ...['unfetter', 'unfrock', 'abash']
    str_columns = [c for c in df.columns if hasattr(df[c], "str")]
    analogy_words = np.unique(df[str_columns].values.reshape((-1,)))
    analogy_words = np.intersect1d(analogy_words, vocab.index.unique())
    is_valid = [df[c].isin(np.unique(vocab.index.values)) for c in str_columns]
    is_valid = np.sum(is_valid, axis=0)
    is_valid = is_valid == len(str_columns)
    return df[is_valid].copy()
