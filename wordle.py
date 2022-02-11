import re
import os
import string
import itertools
import random
import pickle
from tqdm import tqdm
from scipy.stats import entropy

all_patterns = list(itertools.product([0,1,2], repeat=5))
with open('words.txt') as ifp:
	dictionary = list(map(lambda x: x.strip(), ifp.readlines()))

if 'pattern_dict.p' in os.listdir('.'):
	pattern_dict = pickle.load(open('pattern_dict.p', 'rb'))
else:
	pattern_dict = {}
	for word in tqdm(dictionary):
		pattern_dict[word] = {}
		for pattern in all_patterns:
			pattern_dict[word][tuple(pattern)] = set()

		for word2 in words:
			pattern = [0, 0, 0, 0, 0]
			for i, l1 in enumerate(word):
				pattern[i] = int(l1 in word2)

			for i, (l1, l2) in enumerate(zip(word, word2)):
				if l1 == l2:
					pattern[i] = 2

			pattern_dict[word][tuple(pattern)].add(word2)
	pickle.dump(pattern_dict, open('pattern_dict.p', 'wb+'))

for _ in range(10):

	WORD_TO_GUESS = random.choice(dictionary)
	print('-'*100)
	print('Word to guess:', WORD_TO_GUESS)

	all_words = set(dictionary)
	for _ in range(6):
		entropies = {}
		for word in tqdm(all_words):
			counts = []
			for pattern in all_patterns:
				matches = pattern_dict[word][tuple(pattern)]
				matches = matches.intersection(all_words)
				counts.append(len(matches))
			entropies[word] = entropy(counts)

		# print([x[0] for x in sorted(entropies.items(), key=lambda x: -x[1])[:10]])
		# guess_word = input('Guessed word (lower caps):                              ')
		# info       = input('Information (0=grey, 1=yellow, 2=green), e.g. 01201:    ')
		# info = tuple(map(int, tuple(info)))

		# guess_word = random.choice([x[0] for x in sorted(entropies.items(), key=lambda x: -x[1])[:10]])
		guess_word = max(entropies.items(), key=lambda x: x[1])[0]
		print('Guessing:', guess_word)
		info = [0, 0, 0, 0, 0]
		for i, l1 in enumerate(guess_word):
			info[i] = int(l1 in WORD_TO_GUESS)

		for i, (l1, l2) in enumerate(zip(guess_word, WORD_TO_GUESS)):
			if l1 == l2:
				info[i] = 2

		print('Info:', info)
		if guess_word == WORD_TO_GUESS:
			print('WIN!')
			print()
			print()
			print()
			break

		words = pattern_dict[guess_word][tuple(info)]
		all_words = all_words.intersection(words)
