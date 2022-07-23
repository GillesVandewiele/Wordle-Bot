import pickle


def get_pattern_dict_fname(chunk_no=None):
    if chunk_no is None:
        suffix = ''
    else:
        suffix = f'_{chunk_no}'
    return f'pattern_dict{suffix}.p'


def load_pattern_dict(chunk_no=None):
    """Load the cache.
    """
    fname = get_pattern_dict_fname(chunk_no)
    return pickle.load(open(fname, 'rb'))


def save_pattern_dict(pattern_dict, chunk_no=None):
    fname = get_pattern_dict_fname(chunk_no)
    pickle.dump(pattern_dict, open(fname, 'wb+'))
    return
