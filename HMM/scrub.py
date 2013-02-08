# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import scipy
from scipy.signal import butter, filtfilt
from scipy import stats
from scipy.cluster import vq

# <codecell>

def fixOffset(npdata, offset=1e8):    
    '''cleans up data with large, instantaneous offsets (intended for Rot)'''
    ndata = np.copy(npdata -npdata[0])
    diffs = np.diff(ndata)
    idxs = np.nonzero(abs(diffs) > offset)
    
    for idx in idxs[0]:
        ndata[idx+1:] = ndata[idx+1:] - diffs[idx]
        
    return ndata

# <codecell>

def arcLength(d, th):
    '''d = 3xn data (x, y, z) converted to arc length.
Movement below th cut to zero, data should be filtered prior'''
    pass

# <codecell>

def holo(data, h):
    '''Calculate time derivative according to holoborodko's 11th order method
http://www.holoborodko.com/pavel/numerical-methods/numerical-derivative/smooth-low-noise-differentiators/
f = the data to be differentiated
h = the step size, or change in time, between each sample'''
    
    df = np.zeros(len(data)) 
    s = 5 #depends on order of holoborodko
    
    pad1 = [2*data[0]]*s - data[s:0:-1]
    pad2 = [2*data[-1]]*s - data[-2:-(s+2):-1]
    f = np.append(np.append(pad1, data),pad2)
    
    for i in range(s, len(data)+s):
        #Real 11th order Holoborodko
        df[i-s] = (322*(f[i+1]-f[i-1])+256*(f[i+2]-f[i-2])+39*(f[i+3]-f[i-3])
            -32*(f[i+4]-f[i-4])-11*(f[i+5]-f[i-5]) ) / (1536*h)
  
    return df

# <codecell>

def lowpass_butter(input_sig=None, N=10, Wn=5, Fs=None, filter_saftey_margin=1.15):
    '''N = filter order, Wn is cutoff frequency, Fs is sampling frequency, safety_marign multiplies 
cutoff frequency to prevent signal wipeout'''
    b, a = scipy.signal.iirfilter(N, filter_saftey_margin*Wn/(Fs/2), btype='low', ftype='butter')
    return scipy.signal.filtfilt(b, a, input_sig)

# <codecell>

def butter_filter(features, snsrs_edge, task, in_place=True):
    '''Filters array of data by column using 10th order Butterworth filter and Fcutoffs computed
in Tim's Thesis. Can run in place or generate new array. 
N = filter order, Wn is cutoff frequency, Fs is sampling frequency, safety_marign multiplies 
cutoff frequency to prevent signal wipeout'''
    N = 10
    filter_saftey_margin = 1.15
    Fs = 30.0 
    if not in_place: featfilt = np.zeros(features.shape) #for creating new variable
    assert type(snsrs_edge) == list, "snsrs_edge must be type list"
    
    for col in range(len(snsrs_edge)):
        #TESTED, CHECKS OUT
        Wn = fcth[snsrs_edge[col]][tasks[task]] #Get cutoff frequency
        b, a = scipy.signal.iirfilter(N, filter_saftey_margin*Wn/(Fs/2), btype='low', ftype='butter')
        
        if in_place: # For in-place calculations
            if len(snsrs_edge) == 1: features[:] = scipy.signal.filtfilt(b, a, features[:].astype(float))
            else: features[:,col] = scipy.signal.filtfilt(b, a, features[:,col].astype(float))
            
        else: # For new copy of features:
            if len(snsrs_edge) == 1: featfilt[:] = scipy.signal.filtfilt(b, a, features[:].astype(float))
            else: featfilt[:,col] = scipy.signal.filtfilt(b, a, features[:,col].astype(float))
        
    return features if in_place else featfilt

# <codecell>

def dRtaArctan(dRta):
    '''(kpi/2)arctan(pi*dQ3/k) where k = 125deg*sec. See Timk Thesis p32'''
    k = 125
    return (k*np.pi/2) * np.arctan(np.pi*dRta/k)

# <codecell>

def fix_offset_between_tests(ids, feature):
    '''When tests are concatenated to create codebooks, offsets between end and begin of tests create large jumps in 
Rot values. When dRot is calculated, these will be amplified. This script removes such offsets in prep for derivation'''
    #ridx = snsrs_edge.index('Rot')#+1 if first column of features is the testid
    for i in range(len(ids)-1):
        if ids[i] != ids[i+1]: #if the ID has changed
            #print ids[i]
            feature[i+1:] = feature[i+1:] - (feature[i+1]-feature[i])
            
    return feature

# <codecell>

#Normalize each feature
def makeThresholds(feat, pctls=[0.5, 2, 98, 99.5]):
    '''Computes percentiles of a given distribution, returned as list
feat must be a 1D vector of values, not a 2D array. Need not be sorted.'''
    if type(pctls) != list: pctls = list(pctls)
    return [stats.scoreatpercentile(feat, p) for p in pctls]
  
    
def findOutliers(feat, lowerpctl, upperpctl):
    '''Find all locations where feature contains data that is 
below lower and above upper'''
    return np.where((feat < lowerpctl) | (feat > upperpctl))[0]
    
def normalize(feat, lowerpctl, upperpctl):
    '''Map feature such that [lowerpctl upperpctl] = [-1 1]'''
    return (feat - lowerpctl) * (2/ (upperpctl-lowerpctl)) - 1
    
def normalizeByColumn(features, thresholds):
    '''features is mxn np.array of separate features, organized as column vectors. 
thresholds is list of lists, or array, that is nx4 (lowerOutlier, lowerNorm, upperNorm, upperOutlier)'''
    assert features.shape[1] == len(thresholds), 'Num of Features and thresholds do not agree.'
    
    for col in range(features.shape[1]):
        features[:,col] = normalize(features[:,col], thresholds[col][1], thresholds[col][2]) 
    return features

# <codecell>

def removeAndNormalize(features, thresholds=None):
    '''combines all steps of normalization'''
    #Find all thresholds
    if not thresholds:
        thresholds = [makeThresholds(features[:,col]) for col in range(features.shape[1])]
        
    #Delete all outliers
    didx = np.empty(0)
    for col in range(features.shape[1]):
        didx = np.append(didx, findOutliers(features[:,col], thresholds[col][0], thresholds[col][3]))
    #Note to self - doesn't matter for delete if indexes listed multiple times. Thanks, Numpy!
    features = np.delete(features, didx, 0) 
    
    #Normalize each feature
    features = normalizeByColumn(features, thresholds)
        
    return features, thresholds

# <headingcell level=5>

# VQ Encoding, Prep 

# <codecell>

def encodeSegments(feat_seg_norm, codebook):
    '''encode segments of mxn shape with codebook of sxn size where s 
is your desired number of codewords from vq'''
    encoded_segments = []
    
    for segment in feat_seg_norm:
        encd, distortion = vq.vq(segment, codebook)
        encoded_segments.append(encd)
    return encoded_segments

# <codecell>

def zipSegments(segments):   
    '''NLTK HMM trainier requires specific input format of 
encoded features. [[(34,''),(45,'')],[...] ] for example. Tuple is
(observed, labeled state) though unsupervised training does not require
known labeled state, thus empty string'''
    for i in range(len(segments)):
        segments[i] = zip(segments[i],['']*len(segments[i]))
    return segments

# <headingcell level=4>

# Constants, Feature Names

# <codecell>

names = ['%Time_V1', 'J1_L', 'J2_L', 'Lin_L', 'Rot_L', 'ThG_L', 'Fg_L', 'J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'ThG_R', 'Fg_R', 'X_L', 'Y_L', 'Z_L', 'X_R', 'Y_R', 'Z_R']
tasks = {'pegtransfer': 0, 'pegtx': 0, 'cutting': 1, 'suturing': 2, 'clipapply': 3}
features = {}
for i in range(len(names)): features[names[i]] = i

mvmtth = { 'J1'  : 0.0193
		 , 'J2'  : 0.0174
		 , 'Lin' : 0.0
		 , 'Rot' : 0.0564
		 , 'ThG' : 0.0733
		 , 'Fg'  : 0.0363
		 , 'X'   : 0.00699
		 , 'Y'   : 0.00565
		 , 'Z'   : 0.00292 }
         
fcth = {'J1'  : [1.78, 1.86, 1.63]
		 , 'J2'  : [1.60, 1.24, 1.24]
		 , 'Lin' : [5.00, 5.00, 5.00]
		 , 'Rot' : [5.00, 5.00, 5.00]
		 , 'ThG' : [3.61, 6.92, 2.54]
		 , 'Fg'  : [3.05, 6.21, 2.37]
		 , 'X'   : [1.57, 1.51, 1.24]
		 , 'Y'   : [1.60, 1.33, 1.51]
		 , 'Z'   : [1.89, 1.89, 1.60] }

gtExp_idxs = {'pegtransfer':[47, 168, 449, 9, 413, 18]
              ,'cutting':[545, 247, 289, 520, 543, 290, 203, 222, 198, 523]
              ,'suturing':[364, 347, 309, 344, 317, 315, 350, 402]
              }
gtExp_keys = {'pegtransfer':['pegtransfer_'+str(idx) for idx in gtExp_idxs['pegtransfer'] ]
              ,'cutting':['cutting_'+str(idx) for idx in gtExp_idxs['cutting'] ]
              ,'suturing':['suturing_'+str(idx) for idx in gtExp_idxs['suturing'] ]
              }
              

# <codecell>


