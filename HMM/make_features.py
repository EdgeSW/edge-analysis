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
from scipy.signal import butter, filtfilt
from datetime import datetime
import matplotlib.pyplot as plt

from HMM.data_wrangling import *
import HMM.scrub as scrub

# <headingcell level=3>

# Filter, scrub data, Compute derivatives 

# <codecell>

features = None

# <codecell>

#Define labels, initial variables
print 'getting features'
dataset = 'timdata'
task = 'pegtransfer'

# Final Features are Vel-dRta-Gr-dQg (dX, dY, dZ, dRta, Fg, Qg, dQg)
snsrs = {'left':['Time','xL', 'yL', 'zL', 'Q3Lrel', 'QgL', 'FgL'] , 'right':['Time','xR', 'yR', 'zR', 'Q3Rrel', 'QgR', 'FgR']}
snsrs_edge = ['Time','X','Y','Z','Rot','ThG','Fg']
feats = ['Time','dX','dY','dZ','dRta','Fg','Qg','dQg']
hand = 'right'
idx = {}; 
for n in snsrs_edge: idx[n] = snsrs_edge.index(n)

try:
    features
except NameError:
    features = None
if features is None:
    print 'Loading data...'
    features = getFeatures(dataset, task, limit=0, sensors=snsrs[hand], order='key, Time', asdict=True)
    
#Should be len 193, 165, 89 for peg, cut, sut
print 'got features of size', len(features)

# <codecell>

#Fix Offsets in Rotation Angle (Tim has already scrubbed this for his dataset)
#features[:,idx['Rot']] = scrub.fix_offset_between_tests(ids, features[:,idx['Rot']])
#features[:,idx['Rot']] = scrub.fixOffset(features[:,idx['Rot']], offffset=125)
#print  np.diff(features[:,idx['Rot']])[np.diff(features[:,idx['Rot']]) > 20]
#plt.plot(features[:,idx['Rot']])

# <codecell>

#Filter using 10th order Butterworth filter and calc'd Fc's
for k, v in features.iteritems():
    #Ignore column 0 - it's Time
    features[k][:,1:] = scrub.butter_filter(v[:,1:], snsrs_edge[1:], task, in_place=True)
    
#Compute derivatives
h = 1.0/30 # 1/Fs
for k, v in features.iteritems():
    features[k][:,idx['X']] = scrub.holo(v[:,idx['X']], h)
    features[k][:,idx['Y']] = scrub.holo(v[:,idx['Y']], h)
    features[k][:,idx['Z']] = scrub.holo(v[:,idx['Z']], h)
    
    features[k][:,idx['Rot']] = scrub.holo(v[:,idx['Rot']], h)
    #### Pass dRot through arctan function to decrease high spikes
    features[k][:,idx['Rot']] = scrub.dRtaArctan(v[:,idx['Rot']])
    ##### Append dQg to end of features
    features[k] = np.column_stack((features[k], scrub.holo(v[:,idx['ThG']], h)))
    
    features[k] = np.array(features[k], dtype=float16)

#print features[features.keys()[1]]

# <headingcell level=4>

# Upload Computed Features to BigQuery

# <codecell>

xx = features['pegtransfer_69'][:10,2] 
print type(xx), type(xx[0])
yy = np.array(xx, dtype=np.float16)
print type(yy), type(yy[0])
print xx[0]
print repr(xx[0])
print yy[0]
print repr(yy[0])

# <codecell>

date = '2013.1.21'
tablename = 'Vel_dRta_Gr_dQg'

upload_features(features, date, dataset, hand, task, tablename)

# <codecell>


