# Common packages
import re
import numpy as np
import pandas as pd
from pprint import pprint
import os
from smart_open import open

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# Spacy for lemmatization
import spacy

import datetime
# Plotting tools
import pyLDAvis
#import pyLDAvis.gensim
import matplotlib as plt

# Nltk for stopwords
import nltk
from nltk.corpus import stopwords

# Logging and warnings
import logging
logging.basicConfig(filename="gensim.log",format="%(asctime)s : %(levelname)s : %(message)s",level=logging.ERROR)
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

# Customized stop words, Re rules to make souce text good quality
cusStpwords=["bitcoin", "would", "be", "day","nbsp","s","style","font","valign","top"]
reRemoves=[r'\S*@\S*\s?',r'<',r'>',r'\'',r'\n']

# Definition for the source of csv or Json for corpora
htmlSorece="https://raw.githubusercontent.com/selva86/datasets/master/newsgroups.json"
preTextPath='mixedComments.csv'
yearlyPosts=["../data/2017_comments.csv","../data/2018_comments.csv","../data/2019_comments.csv"]

# Get stop words and extended
def getStpwords():
    stwords=stopwords.words("english")
    stwords.extend(cusStpwords)
    return stwords

# Get source corpara
def getNews(filePath):
    if os.path.exists(filePath):
        #,nrows=500
        return pd.read_csv(filePath)

# Clean the corpara with RE
def REremove(ls:list,pos):
    out=[]
    for l in ls:
        t=l[pos]
        for r in reRemoves:
            t=re.sub(r,"",t)
        out.append(t)
    return out

# Sentence to words for making corpora, a generator
def sent2words(ls:list):
    for l in ls:
        yield simple_preprocess(str(l),deacc=True)

# Define functions for stopwords, bigrams, trigrams and lemmatization
def remove_stopwords(texts,stop_words):
    out=[]
    for words in texts:
        t=[]
        for w in words:
            if w not in stop_words:
                t.append(w)
        out.append(t)
    return out


def make_bigrams(texts,bigram_mod):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts,bigram_mod,trigram_mod):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

def lemmatization(texts,nlp, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

def getTrainLDA(interNum,filePath,topicNumber,chunksize=500):
    interNum=str(interNum)
    print("This is the {0} iteration and starts at:".format(interNum))
    print(datetime.datetime.now().strftime("%Y - %m - %d  %H:%M:%S"))
    newsdf=getNews(filePath)
    #Generating stopwords list, ready for cleaning
    stpwords=getStpwords()
    #Changing table to list for fast processing
    newsls=newsdf.values.tolist()
    #Clean the words with regular expressions
    newsls=REremove(newsls,2)
    #Change sentences in to words list, remove punctuations.
    ls_words=list(sent2words(newsls))
    #Create bigram and trigram models for further processing
    bigram = gensim.models.Phrases(ls_words, min_count=5, threshold=100)
    trigram = gensim.models.Phrases(bigram[ls_words], threshold=100)
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    #Remove stopwords
    ls_words_rmstop=remove_stopwords(ls_words, stpwords)
    #Generate Bigrams for the ls_words
    ls_words_bigrams=make_bigrams(ls_words_rmstop, bigram_mod)
    #Inital spacy en model, keep only tagger components for fast processing
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    ls_words_lemma=lemmatization(ls_words_bigrams,nlp)
#Modeling 1 creating dictionaries
    #Create dictionaries and corpus for LDA model
    id2word=corpora.Dictionary(ls_words_lemma)
    #Create corpus
    texts=ls_words_lemma
    #Create TDF
    corpus=[id2word.doc2bow(text) for text in texts]
    # print(corpus[:1])
    # print([[(id2word[id], freq) for id, freq in cp] for cp in corpus[:1]])
#Building the LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=topicNumber,
                                           random_state=100,
                                           update_every=100,
                                           chunksize=chunksize,
                                           passes=18,
                                           alpha='auto',
                                           per_word_topics=True)
    #To see the topics in the LDA model
    lda_model.save("lda_model_"+interNum+"_"+str(topicNumber))
    pprint(lda_model.print_topics())
    doc_lda = lda_model[corpus]
#Model assessment
    # Compute Perplexity
    print('\nPerplexity: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.
# Compute Coherence Score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=ls_words_lemma, dictionary=id2word, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()
    print('\nCoherence Score: ', coherence_lda)
    print(datetime.datetime.now().strftime("%Y - %m - %d  %H:%M:%S"))
    return interNum,topicNumber,lda_model.log_perplexity(corpus),coherence_lda,lda_model.print_topics()

if __name__=="__main__":
    topics=range(12,19,2)
    i=0
    out=[]
    for y in yearlyPosts:
        iterNum,tNum,perP,coHerence,topics=getTrainLDA(i,y,6)
        out.append([iterNum,tNum,perP,coHerence,topics])
        i+=1
    df = pd.DataFrame(out)
    df.to_csv("years_result.csv")



