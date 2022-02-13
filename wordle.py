import os
import itertools
import random
import pickle
from tqdm import tqdm
from scipy.stats import entropy
from collections import defaultdict, Counter

N_GAMES = 10
N_GUESSES = 6
WORD_LEN = 5
DICT_FILE = 'words.txt'


def calculate_pattern(guess, true):
    """Generate a pattern list that Wordle would return if you guessed
    `guess` and the true word is `true` (Thanks to MarkCBell)
    >>> calculate_pattern('weary', 'crane')
    (0, 1, 2, 1, 0)
    >>> calculate_pattern('meets', 'weary')
    (0, 2, 0, 0, 0)
    """
    yellows = Counter(true)
    pattern = []
    for x, y in zip(guess, true):
        if x == y:
            pattern.append(2)
        elif yellows[x] > 0:
            pattern.append(1)
        else:
            pattern.append(0)
        yellows[x] -= 1
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


# Generate the possible patterns of information we can get
all_patterns = list(itertools.product([0, 1, 2], repeat=WORD_LEN))

# Load our dictionary
with open(DICT_FILE) as ifp:
    dictionary = list(map(lambda x: x.strip(), ifp.readlines()))

# Calculate the pattern_dict and cache it, or load the cache.
if 'pattern_dict.p' in os.listdir('.'):
    pattern_dict = pickle.load(open('pattern_dict.p', 'rb'))
else:
    pattern_dict = generate_pattern_dict(dictionary)
    pickle.dump(pattern_dict, open('pattern_dict.p', 'wb+'))

# Simulate games
for _ in range(N_GAMES):

    # Pick a random word for the bot to guess
    WORD_TO_GUESS = random.choice(dictionary)
    print('-'*100)
    print('Word to guess:', WORD_TO_GUESS)

    # Keep a list of the remaining possible words
    all_words = set(dictionary)
    for n_round in range(N_GUESSES):
        # Calculate entropies
        if len(all_words) < 10:
            candidates = all_words
        else:
            candidates = dictionary
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
