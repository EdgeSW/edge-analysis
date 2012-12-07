# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')
from datetime import datetime
from scoring import *
import scipy.cluster.vq as vq
import nltk, pdb
import pickle, cStringIO, ast, json, os
import fetch.shapeS3 as shape
import fetch.fetchS3 as fetchS3
import pickle
from collections import defaultdict

%load_ext autoreload
%autoreload 2

# <headingcell level=4>

# Load the Data

# <codecell>

h = scoring.HMM()
h.load(path='C:\\Users\\Tyler\\.ipython\\Simscore-Computing\\')

# <codecell>

'''load data from local file'''
from numpy import genfromtxt

#'Time' 'Q1L' 'Q2L' 'dL' 'Q3L-rel' 'QgL' 'FgL' 'Q1R' 'Q2R' 'dR' 'Q3R-rel' 'QgR' 'FgR' 'xL' 'yL' 'zL' 'xR' 'yR' 'zR'
#exam_rawdata = genfromtxt(r'C:\Users\Tyler\Google Drive\CSVs\LSU_Subj205_Suturing_01.27.2011-11.05.41_EDGE3.txt', delimiter=',') #A true Novice
#exam_rawdata = genfromtxt(r'C:\Users\Tyler\Google Drive\CSVs\LSU_Subj223_Suturing_01.29.2011-15.13.30_EDGE3.txt ', delimiter=',')# A true Expert

filename = 'edge6/2012/10/24.21.59.05.325.0.txt'
bucketname = 'incoming-simscore-org'
is_secure = False if '.' in bucketname else True
exam_rawdata, meta = shape.getData(filename, bucketname, is_secure=is_secure)



# <codecell>

def p(a,b):
    return a, b

a = p(3,6)
print a

# <headingcell level=4>

# Prep the Data

# <codecell>

type(FgLR)

# <codecell>

'''Segment the data to be scored'''
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


