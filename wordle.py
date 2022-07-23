#!/usr/bin/python
import os
import itertools
import random
import pickle
from tqdm import tqdm
from scipy.stats import entropy
from collections import defaultdict, Counter

N_GUESSES = 10
DICT_FILE_all = 'all_words.txt'
DICT_FILE = 'words.txt'
SAVE_TIME = False

def calculate_pattern(guess, true):
    """Generate a pattern list that Wordle would return if you guessed
    `guess` and the true word is `true`
    Thanks to MarkCBell, Jeroen van der Hooft and gbotev1
    >>> calculate_pattern('weary', 'crane')
    (0, 1, 2, 1, 0)
    >>> calculate_pattern('meets', 'weary')
    (0, 2, 0, 0, 0)
    >>> calculate_pattern('rower', 'goner')
    (0, 2, 0, 2, 2)
    """
    wrong = [i for i, v in enumerate(guess) if v != true[i]]
    counts = Counter(true[i] for i in wrong)
    pattern = [2] * 5
    for i in wrong:
        v = guess[i]
        if counts[v] > 0:
            pattern[i] = 1
            counts[v] -= 1
        else:
            pattern[i] = 0
    return tuple(pattern)


def generate_pattern_dict(dictionary):
    """For each word and possible information returned, store a list
    of candidate words
    >>> pattern_dict = generate_pattern_dict(['weary', 'bears', 'crane'])
    >>> pattern_dict['crane'][(2, 2, 2, 2, 2)]
    {'crane'}
    >>> sorted(pattern_dict['crane'][(0, 1, 2, 0, 1)])
    ['bears', 'weary']
    """
    pattern_dict = defaultdict(lambda: defaultdict(set))
    for word in tqdm(dictionary):
        for word2 in dictionary:
            pattern = calculate_pattern(word, word2)
            pattern_dict[word][pattern].add(word2)
    return dict(pattern_dict)


def calculate_entropies(words, possible_words, pattern_dict):
    """Calculate the entropy for every word in `words`, taking into account
    the remaining `possible_words`"""
    entropies = {}
    for word in words:
        counts = []
        for pattern in all_patterns:
            matches = pattern_dict[word][pattern]
            matches = matches.intersection(possible_words)
            counts.append(len(matches))
        entropies[word] = entropy(counts)
    return entropies


def main():
    # load all 5-letter-words for making patterns 
    with open(DICT_FILE_all) as ifp:
        all_dictionary = list(map(lambda x: x.strip(), ifp.readlines()))

    # Load 2315 words for solutions
    with open(DICT_FILE) as ifp:
        dictionary = list(map(lambda x: x.strip(), ifp.readlines()))

    error_msg = 'Dictionary contains different length words.'
    assert len({len(x) for x in all_dictionary}) == 1, error_msg
    print(f'Loaded dictionary with {len(all_dictionary)} words...')
    WORD_LEN = len(all_dictionary[0]) # 5-letters 

    # Generate the possible patterns of information we can get
    all_patterns = list(itertools.product([0, 1, 2], repeat=WORD_LEN))

    # Calculate the pattern_dict and cache it, or load the cache.
    if 'pattern_dict.p' in os.listdir('.'):
        pattern_dict = pickle.load(open('pattern_dict.p', 'rb'))
    else:
        pattern_dict = generate_pattern_dict(all_dictionary)
        pickle.dump(pattern_dict, open('pattern_dict.p', 'wb+'))

    # Simulate games
    stats = defaultdict(list)

    for WORD_TO_GUESS in tqdm(dictionary):

        if SAVE_TIME:
            guess_word = 'tares'
            all_words = set(all_dictionary)
            info = calculate_pattern(guess_word, WORD_TO_GUESS)
            words = pattern_dict[guess_word][info]
            all_words = all_words.intersection(words)
            init_round = 1
        else:
            all_words = set(all_dictionary)
            init_round = 0

        for n_round in range(init_round, N_GUESSES):

            candidates = all_dictionary
            entropies = calculate_entropies(candidates, all_words, pattern_dict)

            if max(entropies.values()) < 0.1:
                candidates = all_words
                entropies = calculate_entropies(candidates, all_words, pattern_dict)

            # Guess the candiate with highest entropy
            guess_word = max(entropies.items(), key=lambda x: x[1])[0]
            info = calculate_pattern(guess_word, WORD_TO_GUESS)

            # Print round information
            print('Guessing:     ', guess_word)
            print('Info:         ', info)
            if guess_word == WORD_TO_GUESS:
                print(f'WIN IN {n_round + 1} GUESSES!\n\n\n')
                break

            # Filter our list of remaining possible words
            words = pattern_dict[guess_word][info]
            all_words = all_words.intersection(words)

if __name__ == "__main__":
    main()
