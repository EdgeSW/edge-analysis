# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext autoreload
%autoreload 2

# <codecell>

import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')
import numpy as np
import scipy
from HMM.data_wrangling import *
import HMM.scrub as scrub
import HMM.segment as segment
import helpers
import json

# <codecell>

#Define labels, initial variables
print 'getting features'
dataset = 'Vel_dRta_Gr_dQg'
task = 'pegtransfer'
# size = size_codebook(task)
# Final Features are Vel-dRta-Gr-dQg (dX, dY, dZ, dRta, Fg, Qg, dQg)
feats = ['dX','dY','dZ','dRta','Fg','Qg','dQg']
hand = 'right'
idx = {}; 
for n in feats: idx[n] = feats.index(n)

#keys = scrub.gtExp_keys[task]
keys = ['pegtransfer_18']

try:
    features
except NameError:
    features = None
if features is None:
    print 'Loading data...'
    features = getFeatures(dataset, sensors=feats, task=task, hand=hand, keys=keys, asdict=True)
    print 'returned features of size', len(features)

# <codecell>

#Load model
trained = helpers.load_pickle('.ipython\\HMM-Train\\models\\'+'_'.join(['model','timdata',task, hand]))
#Load codebook
fh = open('.ipython\\HMM-Train\\codebooks\\'+'_'.join(['cdbk','timdata',dataset,task, hand,'v1']), 'r')
codebook = json.loads(fh.read())
fh.close()

# <codecell>

#segment, normalize data

# <codecell>

'''Compute log probability of each grasp segment for each hand'''
#For each segment in the Left Hand
logprobNovL = 0; logprobExpL = 0; i=0
start = datetime.now()

def score_log_prob(cdbk, seg_encod):
    lp = cdbk.log_probability( [(t,None) for t in seg_encod]) / len(seg_encod)
    if lp > -1e290:
        return lp
    else: 
        print 'segment %d shows zero probability' %i
        return 0
    
    
for seg in graspsegsLR['left']:
    print i; 
    #Encode the data
    seg_encod, dist = vq.vq(seg, sut_cdbkL)
    
    logprobNovL += score_log_prob(suturingNovL, seg_encod)
    logprobExpL += score_log_prob(suturingExpL, seg_encod)
    i += 1
print logprobNovL, logprobExpL

print datetime.now() - start

