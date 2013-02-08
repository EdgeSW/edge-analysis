# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext autoreload
%autoreload 2

# <codecell>

import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')
from scipy.cluster import vq
import numpy as np
import json
import scipy
from scipy import stats
from scipy.signal import butter, filtfilt
from datetime import datetime
import matplotlib.pyplot as plt
import scipy.cluster as cluster

from HMM.data_wrangling import *
import HMM.scrub as scrub

# <headingcell level=3>

# Compute K-Means Codebook 

# <codecell>

del features
features=None

# <codecell>

#Define labels, initial variables
print 'getting features'
dataset = 'Vel_dRta_Gr_dQg'
task = 'pegtransfer'
size = size_codebook(task)
# Final Features are Vel-dRta-Gr-dQg (dX, dY, dZ, dRta, Fg, Qg, dQg)
snsrs = {'left':['xL', 'yL', 'zL', 'Q3Lrel', 'QgL', 'FgL'] , 'right':['xR', 'yR', 'zR', 'Q3Rrel', 'QgR', 'FgR']}
feats = ['dX','dY','dZ','dRta','Fg','Qg','dQg']
hand = 'right'
idx = {}; 
for n in feats: idx[n] = feats.index(n)

try:
    features
except NameError:
    features = None
if features is None:
    print 'Loading data...'
    ids, features = getFeatures(dataset, task=task, limit=0, sensors=feats, hand=hand, asdict=False)

# <codecell>

#Plot histogram of data from before and after normalization
plt.figure(figsize=(14,16))
cols = features.shape[1]
for col in range(cols):
    subplot(cols,2,2*col+1)
    a = plt.hist(features[:,col],30)
    plt.title(feats[col])
    
features, thresholds = scrub.removeAndNormalize(features)

cols = features.shape[1]
for col in range(cols):
    subplot(cols,2,2*col+2)
    a = plt.hist(features[:,col],30,color='r')
    plt.title(feats[col]+'norm')    

# <codecell>

print thresholds
f = open('thresholds/thresholds_pegtransfer_right_timdata', 'w')
f.write(json.dumps(thresholds))
f.close()

# <headingcell level=2>

# Make Codebooks

# <codecell>

#Start up IPClient
print 'starting client'
from IPython.parallel import Client
ipclient = Client('/home/ubuntu/.starcluster/ipcluster/simcluster-us-east-1.json'
            ,sshkey='/home/ubuntu/.ssh/simcluster.rsa'
            ,packer='pickle')
ipview = ipclient[:]

# <codecell>

def create_codebook(args):
    features, size, i = args
    import scipy.cluster as cluster
    return cluster.vq.kmeans(features, size, 1, 5e-4)


print 'starting timing'
start = datetime.now()
print start
time.sleep(0.5)

run_view = ipview.map_async(create_codebook, [(features, size, i) for i in range(50)])
results = run_view.get()
print datetime.now()-start

# <codecell>

#500 iterations on all rows of data
a = hist([xx[1] for xx in results],15)

# <codecell>

def calcDistortion(features, encoded_features, cdbk):
    myd = []
    for i in range(features.shape[0]):
        myd.append( np.sum((features[i,:] -  cdbk[encoded_features[i]])**2) )
        
    foo = sqrt(myd)
    return mean(foo, axis=-1)

# <codecell>

#resultsR = ipview.map_async(create_codebook, [(featuresR, size, i) for i in range(100)])
lowest_distortion = min(results, key=itemgetter(1))
#lowest_distortion_right = min(results[1], key=itemgetter(1))
#json.dump(lowest_distortion[0].tolist(),  open('{0}_tim_codebook_{1}_VeldRta_Gr_dQg_thresh'.format(hand,task), 'w'))
json.dump(lowest_distortion[0].tolist(),  open('codebooks/cdbk_timdata_{0}_{1}_{2}_v1'.format(dataset, task, hand), 'w'))

#Note that tim had distortion of 0.233 for PegTx L size 57
print 'distortion:', lowest_distortion[1]
#print 'codebook', lowest_distortion[0]

# <codecell>


