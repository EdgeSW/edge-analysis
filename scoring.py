# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from collections import defaultdict

def getGrasps(seg_idxs, exam_rawdata):
    """given the computed segmented indices and the relevant test data, return only data within those indices"""
    graspsegs = defaultdict(list)
    
    try: #Get grasps for left side, checking there are left indices
        graspsegs['left'] = []
        graspsegs['right'] = []
        
        for i in range(len(seg_idxs[0])):
            graspsegs['left'].append(exam_rawdata[:,5:7][seg_idxs[0][i,0]:seg_idxs[0][i,1]]  )
        for i in range(len(seg_idxs[1])):
            graspsegs['right'].append(exam_rawdata[:,11:13][seg_idxs[1][i,0]:seg_idxs[1][i,1]]  )
    except Exception as e:
        print e
    
    return graspsegs

# <codecell>

import numpy as np
#def segment(args):
def segment_exam(task, arr):
    """Given the task and a """
    #task, thresholds, kv = args
    thresholds = {'suturing': (1.5, 0.1*30), 'cutting': (3, 0.5*30), 'pegtransfer': (3, 1*30)} 
    task_threshold = thresholds.get(task, (0, 0))
    
    #arr = arr.astype(float) #Convert from unicode to float
    
    lidx, = np.diff(arr[:, 0] > task_threshold[0]).nonzero()
    lidx = np.delete(lidx,-1) if len(lidx)%2==1 else lidx
    lidx = np.append(np.matrix(lidx[range(0,len(lidx),2)]).transpose(), np.matrix(lidx[range(1,len(lidx),2)]).transpose() , 1)
    lidx = np.squeeze(np.asarray(lidx)) #lidx = lidx.shape(-1,2) #puts idx into a two column matrix

    ridx, = np.diff(arr[:, 1] > task_threshold[0]).nonzero()
    ridx = np.delete(ridx,-1) if len(ridx)%2==1 else ridx
        
    ridx = np.append(np.matrix(ridx[range(0,len(ridx),2)]).transpose(), np.matrix(ridx[range(1,len(ridx),2)]).transpose() , 1)
    ridx = np.squeeze(np.asarray(ridx)) #ridx = ridx.shape(-1,2) #puts idx into a two column matrix

    #Check to make sure grasp is longer than time thresh:: IndexError: invalid index
    e = None
    try:
        left =  lidx[lidx[:, 1] - lidx[:, 0] > task_threshold[1]]
    except Exception as e:
        left = None
    
    try:
        right = ridx[ridx[:, 1] - ridx[:, 0] > task_threshold[1]]
    except Exception as e:
        right = None 
    
    return (left, right, e)

# <codecell>

def download_codebook(date):
    qs = "SELECT dataset, task, json FROM data.codebooks WHERE date ='{0}'".format('10-OCT-2012 1:33')
    data = queryGoogle(qs)
    
    cdbkL = data['rows'][0]['f'][2]['v']
    cdbkR = data['rows'][1]['f'][2]['v'] 
    cdbkL = np.array(json.loads(cdbkL))
    cdbkR = np.array(json.loads(cdbkR))
    
    dataset = str(data['rows'][0]['f'][0]['v'])
    task = str(data['rows'][0]['f'][1]['v'] )
        
    return cdbkL, cdbkR, dataset, task

# <codecell>

def score_test(jsonSimscore):
    return None

# <codecell>


