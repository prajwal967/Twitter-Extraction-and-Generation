from __future__ import print_function
import numpy as np
import random
import sys
import re
import json

__all__ = ["ParseTweets", "BuildCorpus"]

#The following is done to tokenize the tweets into its appropriate form
#In particular, we try to capture some emoticons, HTML tags, Twitter @usernames (@-mentions), Twitter #hashtags, 
#URLs, numbers, words with and without dashes and apostrophes

#Source : https://marcobonzanini.com/2015/03/09/mining-twitter-data-with-python-part-2/
class ParseTweets():
    
    def __init__(self):
        
        self.emoticons_str = r"""
        (?:
            [:=;] # Eyes
            [oO\-]? # Nose (optional)
            [D\)\]\(\]/\\OpP] # Mouth
        )"""
        self.regex_str = [
        self.emoticons_str,
        r'<[^>]+>', # HTML tags
        r'(?:@[\w_]+)', # @-mentions
        r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
        r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs

        r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
        r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
        r'(?:[\w_]+)', # other words
        r'(?:\S)' # anything else
        ]
        
        self.tokens_re = re.compile(r'(' + '|'.join(self.regex_str) + ')', re.VERBOSE | re.IGNORECASE)
        self.emoticon_re = re.compile(r'^' + self.emoticons_str + '$', re.VERBOSE | re.IGNORECASE)
        
    def tokenize(self, text):
        return self.tokens_re.findall(text)
    
    def preprocess(self, text, lowercase = False):
        tokens = self.tokenize(text)
        if lowercase:
            tokens = [token if self.emoticon_re.search(token) else token.lower() for token in tokens]
        return tokens
    
    def parse_tweets(self, filename, lowercase):
        
        text = ''
        with open(filename, 'r') as file:
            for line in file:

                tweet = json.loads(line) # load it as Python dict
                tokens = self.preprocess(tweet['text'], lowercase)

                for index,element in enumerate(tokens):

                    #Removing '#' 
                    if('#' in element):

                        del tokens[index]
                        text = text + ""
                        continue


                    #Removing the 'RT' tag
                    elif('RT' in element):

                        del tokens[index]
                        text = text + ""
                        continue

                    #This character usually follows the 'RT' tag, so we remove it
                    elif(':' in element):

                        del tokens[index]
                        text = text + ""
                        continue

                    text = text + " " + tokens[index]
                    
        return text

class BuildCorpus():
    
    def __init__(self, text):
        self.chars = sorted(list(set(text)))
        self.char_indices = dict((c, i) for i, c in enumerate(self.chars))
        self.indices_char = dict((i, c) for i, c in enumerate(self.chars))
        self.sentences = list()
        self.next_chars = list()
        self.maxlen = 0
        self.step = 0
        self.text = text
        
    def build_sentences(self, maxlen = 40, step = 1):
        # cut the text in semi-redundant sequences of maxlen characters
        self.maxlen = maxlen
        self.step = step
        for i in range(0, len(self.text) - self.maxlen, self.step):
            self.sentences.append(self.text[i: i + maxlen])
            self.next_chars.append(self.text[i + maxlen])
            
    def vectorize_text(self):
        
        X = np.zeros((len(self.sentences), self.maxlen, len(self.chars)), dtype=np.bool)
        Y = np.zeros((len(self.sentences), len(self.chars)), dtype=np.bool)
        for i, sentence in enumerate(self.sentences):
            for t, char in enumerate(sentence):
                X[i, t, self.char_indices[char]] = 1
            Y[i, self.char_indices[self.next_chars[i]]] = 1
            
        return X, Y