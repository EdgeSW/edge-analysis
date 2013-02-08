# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <rawcell>

# Tim's Thresholds:
# #GrspVarTh{PegTx}    = [ 3 3   3 3    1];   %{Qo Qc Fo Fc Tth];
# #GrspVarTh{Suturing} = [ 4 3   3 3    .1];  %{Qo Qc Fo Fc Tth]; 
# #GrspVarTh{Cutting}  = [ 3 3  1.5 1.5 .5];  %{Qo Qc Fo Fc Tth]; 

# <codecell>

import numpy as np
import json, sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')

# <codecell>

fg_thresholds = {'suturing': (1.5, 0.1*30), 'cutting': (3, 0.5*30), 'pegtransfer': (3, 1*30)} 

# <headingcell level=3>

# Segmentation By Fg

# <codecell>

def getSplitIdxs(force, task, thresholds):
    '''Given a vector (could be Fg, Qg, etc), returns the indexes of when vector is greater than the 
the threshold defined for that task in thresholds. Returns segidx_list as list of 
separated np.arrays for each separate force>thresh segment.'''
    #Determine the indexes where force is greater than threshold, segment
    idxs_above_thresh = (force > thresholds[task][0]).nonzero()[0]
    cuts = (np.diff(idxs_above_thresh) > 1).nonzero()[0] + 1
    segidx_list = np.split(idxs_above_thresh, cuts)
    
    #Remove segment if shorter than time threshold
    for i in range(len(segidx_list)-1, -1, -1):#count backwards to avoid IndexError
        if len(segidx_list[i]) <= thresholds[task][1]:
            segidx_list.pop(i)
    return segidx_list



def pullSegments(features, segidx_list):
    '''given a list of np.arrays containing indexes of desired data, splits
features into a list of arrays as well, returning all columns. 
EXAMPLE: segidx_list = [[3,4,5,6],[10,11,12],[30,31,32]...]
         returns: [features[[3,4,5,6],:],features[[10,11,12],:],...] 
    '''
    return [features[seg,:] for seg in segidx_list]

# <codecell>

def segmentFeatures(features, task, idx_of_feat_used_to_thresh, thresholds):
    '''wrapper/combination for getSplitIdxs and pullSegments'''
    segidx_list = getSplitIdxs(features[:, idx_of_feat_used_to_thresh], task, thresholds)
    return pullSegments(features, segidx_list)


def segmentDictOfTests(feat_dict, task, idx_to_thresh, thresholds=fg_thresholds):
    '''performs segmentFeatures for a list of Tests, returning a 
dictionary with same keys as input dict'''
    seg_data_by_force = {}
    for k, v in feat_dict.iteritems():
        seg_data_by_force[k] = segmentFeatures(v, task, idx_to_thresh, thresholds)
    return seg_data_by_force


def segmentDictOfTestsAsList(feat_dict, task, idx_to_thresh, thresholds=fg_thresholds):
    '''performs segmentFeatures for a list of Tests, returning a list of segs'''
    list_to_return = []
    for k, v in feat_dict.iteritems():
        for item in segmentFeatures(v, task, idx_to_thresh, thresholds): list_to_return.append(item)
        #list_to_return.append([segment for segment in segmentFeatures(v, task, idx_to_thresh, thresholds)])
    return list_to_return
    #return [segmentFeatures(v, task, idx_to_thresh, thresholds) for k, v in feat_dict.iteritems()]

# <codecell>


