# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext autoreload
%autoreload 2
from datetime import datetime
from scoring import *
import scipy.cluster.vq as vq
import nltk, pdb
import pickle, cStringIO, ast, json, os
import scoring as scoring
import fetch.shapeS3 as shape
import fetch.fetchS3 as fetchS3
import pickle

# <headingcell level=4>

# Load the Data

# <codecell>

def load_pickle(filepath):
    '''opens and closes pickled file and returns contained pickleobj'''
    #try:
    f = open(filepath, 'r')
    var = pickle.load(f)
    f.close()
    return var    

# <codecell>

### Get Codebook if Needed
if 'C:\\' in os.getcwd(): prefix = 'C:\\Users\\Tyler\\.ipython\\Simscore-Computing\\'
else: prefix = ''
l = 'sut_cdbkL'
r = 'sut_cdbkR'

sut_cdbkL = load_pickle(prefix+l)
sut_cdbkR = load_pickle(prefix+r)


###Open Saved HMM 
suturingNovL = load_pickle(prefix+'suturingNovL')
suturingExpL = load_pickle(prefix+'suturingExpL')

print suturingExpL

# <codecell>

'''import pickle
# now create a file
# replace filename with the file you want to create
file = open('sut_cdbkR', 'w')
# now let's pickle picklelist
pickle.dump(sut_cdbkR,file)
# close the file, and your pickling is complete
file.close()'''


# <codecell>

'''load data from local file'''
from numpy import genfromtxt

#'Time' 'Q1L' 'Q2L' 'dL' 'Q3L-rel' 'QgL' 'FgL' 'Q1R' 'Q2R' 'dR' 'Q3R-rel' 'QgR' 'FgR' 'xL' 'yL' 'zL' 'xR' 'yR' 'zR'
#exam_rawdata = genfromtxt(r'C:\Users\Tyler\Google Drive\CSVs\LSU_Subj205_Suturing_01.27.2011-11.05.41_EDGE3.txt', delimiter=',') #A true Novice

'''filename = 'edge6/2012/10/24.21.59.05.325.0.txt'
bucketname = 'incoming-simscore-org'
is_secure = False if '.' in bucketname else True
exam_rawdata, meta = shape.getData(filename, bucketname, is_secure=is_secure)'''

exam_rawdata = genfromtxt(r'C:\Users\Tyler\Google Drive\CSVs\LSU_Subj223_Suturing_01.29.2011-15.13.30_EDGE3.txt ', delimiter=',')# A true Expert

# <headingcell level=4>

# Prep the Data

# <codecell>

'''Segment the data that will be scored'''
FgLR = exam_rawdata[:,[6,12]]
seg_idxs = segment_exam('suturing',FgLR)

graspsegsLR = getGrasps(seg_idxs, exam_rawdata)


# <headingcell level=4>

# Score the Data

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

# <codecell>

#vq.vq(graspsegsLR['left'][3], cdbkL) #WHY is that one number so small...it's clearly the log of zero
if 2**(-4.04858299595e+297) < 1e-100:
    print 'small'
else: print 'big'

# <headingcell level=2>

# Functions

# <codecell>

type([('33',None)])

# <codecell>


# <codecell>


