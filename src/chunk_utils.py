from src.disk_utils import load_pattern_dict

CHUNK_SIZE = 5000


def chunks(lst, n=CHUNK_SIZE):
    """Yield successive n-sized chunks from lst.
    Reference: https://stackoverflow.com/a/312464/376454
    """
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def get_num_chunks(lst):
    return int(len(lst) / CHUNK_SIZE) + 1


def find_chunk_no(large_list, element):
    for chunk_no, small_list in enumerate(chunks(large_list), start=1):
        if element in small_list:
            return chunk_no
    return None


def get_pattern(all_dictionary, guess_word):
    chunk_no = find_chunk_no(all_dictionary, guess_word)
    pattern_dict = load_pattern_dict(chunk_no)
    return pattern_dict[guess_word]
