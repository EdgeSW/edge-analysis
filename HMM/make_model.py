# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ###Introduction:
# 
# In order to grade physicians’ performance on specific tasks a model of good and novice physicians must be created.  The specific steps to create this model are:  
# 1.  Vector Quantization: reducing the total number of dimensions and normalizing the data  
# 2.  Feature Segmentation: looking only at data while grasping objects  
# 3.  Push to HMM training   

# <codecell>

%load_ext autoreload
%autoreload 2

# <codecell>

import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')
from scipy.cluster import vq
import numpy as np
import json, copy
import scipy
import nltk

from datetime import datetime
import matplotlib.pyplot as plt
import scipy.cluster as cluster
from HMM.data_wrangling import *
import HMM.myBigQuery as myBQ
import HMM.scrub as scrub
import HMM.segment as segment

# <headingcell level=4>

# Get Data

# <codecell>

features = None

# <codecell>

#Define labels, initial variables
print 'getting features'
dataset = 'Vel_dRta_Gr_dQg'
task = 'pegtransfer'
size = size_codebook(task)
# Final Features are Vel-dRta-Gr-dQg (dX, dY, dZ, dRta, Fg, Qg, dQg)
feats = ['dX','dY','dZ','dRta','Fg','Qg','dQg']
hand = 'right'
idx = {}; 
for n in feats: idx[n] = feats.index(n)

keys = scrub.gtExp_keys[task]

try:
    features
except NameError:
    features = None
if features is None:
    print 'Loading data...'
    features = getFeatures(dataset, sensors=feats, task=task, hand=hand, keys=keys, asdict=True)
    print 'returned features of size', len(features)

# <headingcell level=4>

# Get VQ Codebook

# <codecell>

#cdbkL, cdbkR, a, b = vqr.download_codebook('10-OCT-2012 1:33')
pp = '.ipython/HMM-Train/codebooks/'+'_'.join(['cdbk','timdata',dataset,task,hand,'v1']) ##LOCAL
#pp = 'codebooks/'+'_'.join(['cdbk','timdata',dataset,task,hand,'v1']) ##UBUNTU

fh = open(pp,'r')
codebook = np.array(json.loads(fh.read()))
fh.close()
print 'codebook size',len(codebook)

# <headingcell level=4>

# Segmentation

# <codecell>

#Get indexes of grasps
#NOTE - force can start above 3.
#Create new dict with keys as filenames and list of np.arrays that are the segments
feat_seg = segment.segmentDictOfTestsAsList(features, task, idx['Fg'])

# <codecell>

##Plot all segments separated by test if you'd like...
for k, v in segment.segmentDictOfTests(features, task, idx['Fg']).iteritems():
    a = plt.figure()
    for seg in v:
        a = plt.plot(seg[:,idx['Fg']])
    a = plt.plot(range(250), [3]*250)

# <codecell>

##Plot all segments if you like...
for segment in feat_seg:
    a = plt.plot(segment[:, idx['Fg']])
a = plt.plot(range(250), [3]*250)

# <headingcell level=4>

# Scrub, Normalize Data

# <codecell>

#Scrub and normalize data for training
### Butter, Holo ...(data is already filtered, derived)
### Remove outliers???
### Normalize

#retrieve thresholds 
pp = '.ipython/HMM-Train/thresholds/'+'_'.join(['thresholds','timdata',task,hand]) ##LOCAL
#pp = 'thresholds/'+'_'.join(['thresholds','timdata',task,hand]) ##UBUNTU

fh = open(pp,'r')
thresholds = json.loads(fh.read())
fh.close()
print 'Loaded thresholds size',len(thresholds)

# <codecell>

def normalizeDictSegments(feat_seg, thresholds):
    '''Return new dict of normalized, segmented features for each test. thresholds
provided must be same as ones used for feat normalization prior to cdbk training'''
    feat_seg_norm = copy.deepcopy(feat_seg)
    for key, test in feat_seg_norm.iteritems():
        for seg in test:
            seg = scrub.normalizeByColumn(seg, thresholds)
    return feat_seg_norm

def normalizeListSegments(feat_seg, thresholds):
    '''Return new list of normalized, segmented features for each test. thresholds
provided must be same as ones used for feat normalization prior to cdbk training'''
    feat_seg_norm = copy.deepcopy(feat_seg)
    
    return [scrub.normalizeByColumn(segment, thresholds) for segment in feat_seg_norm]


feat_seg_norm = normalizeListSegments(feat_seg, thresholds)

print feat_seg_norm[0][:5]

# <headingcell level=4>

# Encode Data

# <codecell>

encoded_segments = scrub.encodeSegments(feat_seg_norm, codebook)

# <codecell>

#Take a visual peek at the distribution of codewords
a,b,c = hist(np.concatenate(tuple([seg for seg in encoded_segments])), size)

# <headingcell level=2>

# Train Model

# <markdowncell>

# Client & View:

# <codecell>

'''from IPython.parallel import Client
#Start up IPClient
print 'starting client'
from IPython.parallel import Client
ipclient = Client('/home/ubuntu/.starcluster/ipcluster/simcluster-us-east-1.json'
            ,sshkey='/home/ubuntu/.ssh/simcluster.rsa'
            ,packer='pickle')
ipview = ipclient[:]
'''
'''def getClient():
    ipclient = Client('/home/ubuntu/.starcluster/ipcluster/simcluster-us-east-1.json'
                      ,sshkey='/home/ubuntu/.ssh/starcluster.rsa'
                      ,packer='pickle')
    ipview = ipclient[:]
    return ipview, ipclient

ipview, ipclient = getClient()
print ipview
print ipclient
'''

# <codecell>

rrr='''s = """"Your humble writer knows a little bit about a lot of things, but despite writing a fair amount about text processing (a book, for example), linguistic processing is a relatively novel area for me. Forgive me if I stumble through my explanations of the quite remarkable Natural Language Toolkit (NLTK), a wonderful tool for teaching, and working in, computational linguistics using Python. Computational linguistics, moreover, is closely related to the fields of artificial intelligence, language/speech recognition, translation, and grammar checking.\nWhat NLTK includes\nIt is natural to think of NLTK as a stacked series of layers that build on each other. Readers familiar with lexing and parsing of artificial languages (like, say, Python) will not have too much of a leap to understand the similar -- but deeper -- layers involved in natural language modeling.\nGlossary of terms\nCorpora: Collections of related texts. For example, the works of Shakespeare might, collectively, by called a corpus; the works of several authors, corpora.\nHistogram: The statistic distribution of the frequency of different words, letters, or other items within a data set.\nSyntagmatic: The study of syntagma; namely, the statistical relations in the contiguous occurrence of letters, words, or phrases in corpora.\nContext-free grammar: Type-2 in Noam Chomsky's hierarchy of the four types of formal grammars. See Resources for a thorough description.\nWhile NLTK comes with a number of corpora that have been pre-processed (often manually) to various degrees, conceptually each layer relies on the processing in the adjacent lower layer. Tokenization comes first; then words are tagged; then groups of words are parsed into grammatical elements, like noun phrases or sentences (according to one of several techniques, each with advantages and drawbacks); and finally sentences or other grammatical units can be classified. Along the way, NLTK gives you the ability to generate statistics about occurrences of various elements, and draw graphs that represent either the processing itself, or statistical aggregates in results.\nIn this article, you'll see some relatively fleshed-out examples from the lower-level capabilities, but most of the higher-level capabilities will be simply described abstractly. Let's now take the first steps past text processing, narrowly construed. """
sentences = s.split('.')[:-1]
seq = [map(lambda x:(x,''), ss.split(' ')) for ss in sentences]
symbols = list(set([ss[0] for sss in seq for ss in sss]))
states = range(5)
trainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=states,symbols=symbols)
m = trainer.train_unsupervised(seq)'''

# <codecell>

#Zip encoded segments into appropriate format
encoded_segments = scrub.zipSegments(encoded_segments)

# <codecell>

start = datetime.now()
print 'Training', task, ': \n', start


nltkTrainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=range(15), symbols=range(codebook.shape[0]))
trained = nltkTrainer.train_unsupervised(encoded_segments, max_iterations=5)

end = datetime.now()
print end
print end - start

# <codecell>

trained_3_iterations = trained
#4 minutes, logprob -37127

# <codecell>

import pickle
# now create a file
# replace filename with the file you want to create
file = open('model_timdata_'+task+'_'+hand, 'w')
# now let's pickle picklelist
pickle.dump(trained,file)
# close the file, and your pickling is complete
file.close()

# <codecell>

###
unpicklefile = open('model_timdata_'+task+'_'+hand, 'r')
# now load the list that we pickled into a new object
unpickledlist = pickle.load(unpicklefile)
# close the file, just for safety
unpicklefile.close()

# <codecell>


