from __future__ import print_function
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import re
import json

from corpus import ParseTweets, BuildCorpus

class LTSM():
    
    def __init__(self):
        self.model = Sequential()
        
    def build_model(self, corpus):
        self.model.add(LSTM(128, input_shape = (corpus.maxlen, len(corpus.chars))))
        self.model.add(Dense(len(corpus.chars)))
        self.model.add(Activation('softmax'))
        optimizer = RMSprop(lr = 0.01)
        self.model.compile(loss = 'categorical_crossentropy', optimizer = optimizer)
        
    def sample(self, preds, temperature = 1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)
        
    def train(self, X, Y, corpus):
        
        # train the model, output generated text after each iteration
        for iteration in range(1, 10):
            print()
            print('-' * 50)
            print('Iteration', iteration)
            self.model.fit(X, Y, batch_size = 128, epochs = 10)

            start_index = random.randint(0, len(corpus.text) - corpus.maxlen - 1)

            for diversity in [0.2, 0.5, 1.0, 1.2]:
                print()
                print('----- diversity:', diversity)

                generated = ''
                sentence = corpus.text[start_index: start_index + corpus.maxlen]
                generated += sentence
                print('----- Generating with seed: "' + sentence + '"')
                print('\nGenerated')
                sys.stdout.write(generated)

                for i in range(20):
                    x = np.zeros((1, corpus.maxlen, len(corpus.chars)))
                    for t, char in enumerate(sentence):
                        x[0, t, corpus.char_indices[char]] = 1.

                    preds = self.model.predict(x, verbose=0)[0]
                    next_index = self.sample(preds, diversity)
                    next_char = corpus.indices_char[next_index]

                    generated += next_char
                    sentence = sentence[1:] + next_char

                    sys.stdout.write(next_char)
                    sys.stdout.flush()
                print()

if __name__ == "__main__":
    
    parse_tweets = ParseTweets()
    text = parse_tweets.parse_tweets('euro_python.json', False)
    corpus = BuildCorpus(text)
    corpus.build_sentences()
    X, Y = corpus.vectorize_text()
    
    ltsm = LTSM()
    ltsm.build_model(corpus)
    ltsm.train(X, Y, corpus)