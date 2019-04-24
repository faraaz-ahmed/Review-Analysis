
# Saved successfully!
# Copy of Sentiment_with_bayes.ipynb
# Copy of Sentiment_with_bayes.ipynb_
 

import numpy as np 

import pandas as pd 

import bz2

import gc

import re

import os

import pickle

# print(os.listdir("../input"))

# from google.colab import drive

# drive.mount('/content/gdrive/')

train_file = bz2.BZ2File('train.ft.txt.bz2','r')

test_file = bz2.BZ2File('test.ft.txt.bz2','r')

train_file_lines = train_file.readlines()

test_file_lines = test_file.readlines()


# del train_file, test_file

gc.collect()


train_file_lines = [x.decode('utf-8') for x in train_file_lines]

test_file_lines = [x.decode('utf-8') for x in test_file_lines]


train_labels = [0 if x.split(' ')[0] == '__label__1' else 1 for x in train_file_lines]

train_sentences = [x.split(' ', 1)[1][:-1].lower() for x in train_file_lines]

for i in range(len(train_sentences)):
    train_sentences[i] = re.sub('\d','0',train_sentences[i])

    

test_labels = [0 if x.split(' ')[0] == '__label__1' else 1 for x in test_file_lines]

test_sentences = [x.split(' ', 1)[1][:-1].lower() for x in test_file_lines]

for i in range(len(test_sentences)):
    test_sentences[i] = re.sub('\d','0',test_sentences[i])
                                                       

for i in range(len(train_sentences)):
    if 'www.' in train_sentences[i] or 'http:' in train_sentences[i] or 'https:' in train_sentences[i] or '.com' in train_sentences[i]:
        train_sentences[i] = re.sub(r"([^ ]+(?<=\.[a-z]{3}))", "<url>", train_sentences[i])
        
for i in range(len(test_sentences)):
    if 'www.' in test_sentences[i] or 'http:' in test_sentences[i] or 'https:' in test_sentences[i] or '.com' in test_sentences[i]:
        test_sentences[i] = re.sub(r"([^ ]+(?<=\.[a-z]{3}))", "<url>", test_sentences[i])


del train_file_lines, test_file_lines

train_sentences[0]

import nltk

from nltk.corpus import stopwords

from nltk.classify import SklearnClassifier

from wordcloud import WordCloud,STOPWORDS

import matplotlib.pyplot as plt

# %matplotlib inline

# Input data files are available in the "../input/" directory.

# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output


Na_train = {'Sentence': train_sentences, 'Label': train_labels}

Nav_train = pd.DataFrame(Na_train)
Na_test = {'Sentence': test_sentences, 'Label': test_labels}
Nav_test = pd.DataFrame(Na_test)
Nav_train.head()

print("*************************** TOTAL LENGTH OF DATAFRAME ************************************* = \n", len(Nav_train.index))

Nav_train = Nav_train.head(100000)
Nav_test = Nav_test.head(1000)
del Na_train, Na_test, train_sentences, train_labels

gc.collect()


# nltk.download('stopwords')

sents = []

# alll = []
# x = "stopwords_set = set(stopwords.words('english'))​"
# print(x)

alll = []
stopwords_set = set(stopwords.words('english'))

for index, row in Nav_train.iterrows():
    words_filtered = [e.lower() for e in row.Sentence.split() if len(e) >= 3]
    words_cleaned = [word for word in words_filtered
        if 'http' not in word
        and not word.startswith('@')
        and not word.startswith('#')
        and word != 'RT']
    words_without_stopwords = [word for word in words_cleaned if not word in stopwords_set]
    sents.append((words_without_stopwords, row.Label))
    alll.extend(words_without_stopwords )


def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    print("***************************************WORD_LIST**********************************", wordlist)
    # Attempt to pickle the ditionary all the best
    with open("results_features_1.pkl", "wb") as output:
            pickle.dump(wordlist, output, protocol = pickle.HIGHEST_PROTOCOL)
            print("*************************************  PICKLING   WAS   SUCCESSFUL  ****************************************")
    features = wordlist.keys()
    return features
w_features = get_word_features(alll)

#Storing the word features object as a pickle
# with open('results_features.pkl', 'wb') as output:
#         pickle.dump(w_features, output, pickle.HIGHEST_PROTOCOL)

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in w_features:
        features['contains(%s)' % word] = (word in document_words)
    return features
training_set = nltk.classify.apply_features(extract_features,sents)

classifier = nltk.NaiveBayesClassifier.train(training_set)

#Storing the classifier object as a pickle
with open('results_classifier_1.pkl', 'wb') as output:
        pickle.dump(classifier, output, pickle.HIGHEST_PROTOCOL)

print("******************************************CLASSIFIER**********************************\n",classifier)
train_pos = Nav_train[Nav_train['Label'] == 1]

train_pos = train_pos['Sentence']

train_neg = Nav_train[Nav_train['Label'] == 0]

train_neg = train_neg['Sentence']

test_pos = Nav_test[Nav_test['Label'] == 1]
test_pos = test_pos['Sentence']

test_neg = Nav_test[Nav_test['Label'] == 0]

test_neg = test_neg['Sentence']

test_neg.head(6)

neg_cnt = 0

pos_cnt = 0
for obj in test_neg: 
    res =  classifier.classify(extract_features(obj.split()))
    if(res == 0): 
        neg_cnt = neg_cnt + 1
for obj in test_pos: 
    res =  classifier.classify(extract_features(obj.split()))
    if(res == 1): 
        pos_cnt = pos_cnt + 1
        
print('[Negative]: %s/%s '  % (len(test_neg),neg_cnt))        
print('[Positive]: %s/%s '  % (len(test_pos),pos_cnt))
acccc= ((neg_cnt+pos_cnt)/(len(test_neg)+len(test_pos))) * 100
print("Accuracy by nltk classifier is", acccc)

print(test_neg.loc[52])
print(classifier.classify(extract_features(test_neg.loc[52].split())))

x = w_features

print('type of x :',type(x))
