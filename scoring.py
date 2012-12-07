# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os

# <codecell>

def load_pickle(filepath, ftype='r'):
    '''opens and closes pickled file and returns contained pickleobj'''
    
    f = open(filepath, ftype)
    contents = pickle.load(f)
    f.close()
    return contents    

# <codecell>

class Score(object):
    '''class container for scoring an EDGE test'''
    def __init__(self, task=None, skill=None, left=0, right=0):
        self.task = task
        self.skill = skill
        self.left = left
        self.right = right
        
    def __add__(self, other):
        if isinstance(other, Score):
            return self.score()+other.score()
        else:
            raise ValueError, 'Not a Score instance'
        
    def score(self):
        return self.left+self.right
        
    
     
class HMM(object):
    '''to easily access all codebooks, trained model for scoring'''
    def __init__(self, codebook=None, model=None):
        self.codebook = codebook
        self.model = model     
        self.tasks = ['pegtransfer','cutting','suturing']
        self.hands = ['left','right']
        self.skills = ['expert','novice']
        
    def load(self, cdbk_ver='v1', model_ver='v1', lf=load_pickle, path=os.getcwd()):
        
        self.codebook = { } 
        self.model = {}
        
        for task in self.tasks:
            self.codebook[task] = {}
            for hand in self.hands:
                fname = '_'.join([task,hand,cdbk_ver])
                try: self.codebook[task][hand] = lf(path+fname)
                except: self.codebook[task][hand] = None
        
        for task in self.tasks:
            self.model[task] = {}
            for hand in self.hands:
                self.model[task][hand] = {}
                for skill in self.skills:
                    fname = '_'.join([task,hand,skill,model_ver])
                    try: self.model[task][hand][skill] = lf(path+fname)
                    except: self.model[task][hand][skill] = None
        

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


