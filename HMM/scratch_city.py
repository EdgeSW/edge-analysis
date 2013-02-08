# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <rawcell>

# HMM Stuff left to Implement:
# 
# * implement derivative calculations (holboloroko)
# * Code to score dataset against model
# * Clean up loading of FgLR to take up less memory (steal from features? load w/ features?)

# <codecell>

%load_ext autoreload
%autoreload 2
from datetime import datetime
import scipy.cluster.vq as vq
import vector_quantization_refactor as vqr
import segmentation_refactor as segr
import data_wrangling_page as dwp
import cStringIO
import json
import nltk
import pickle
import pycurl
import cStringIO
import ast

# <codecell>

c = pycurl.Curl()
c = dwp.loginSimscore(c)
aua = dwp.getSkillSimscore(c)
print aua
c = dwp.logoutSimscore(c)

# <codecell>

def log_likelihood(classifier, gold):
    results = classifier.batch_prob_classify([fs for (fs,l) in gold])
    ll = [pdist.prob(l) for ((fs,l), pdist) in zip(gold, results)]
    return math.log(float(sum(ll))/len(ll))

# <headingcell level=1>

# Scoring Code

# <codecell>

from nltk.tag.hmm import *
symbols = ['up', 'down', 'unchanged']
states = ['bull', 'bear', 'static']

def probdist(values, samples):
     d = {}
     for value, item in zip(values, samples):
         d[item] = value
     return DictionaryProbDist(d)

def conditionalprobdist(array, conditions, samples):
     d = {}
     for values, condition in zip(array, conditions):
         d[condition] = probdist(values, samples)
     return DictionaryConditionalProbDist(d)

A = array([[0.6, 0.2, 0.2], [0.5, 0.3, 0.2], [0.4, 0.1, 0.5]], float64)
A = conditionalprobdist(A, states, states)
 	
B = array([[0.7, 0.1, 0.2], [0.1, 0.6, 0.3], [0.3, 0.3, 0.4]], float64)
B = conditionalprobdist(B, states, symbols)
pi = array([0.5, 0.2, 0.3], float64)
pi = probdist(pi, states)
 	
model = HiddenMarkovModelTagger(symbols=symbols, states=states,transitions=A, outputs=B, priors=pi)
 	
test = ['up', 'down', 'up']
sequence = [(t, None) for t in test]
 	
print '%.3f' % (model.probability(sequence))

model.tag(test)

