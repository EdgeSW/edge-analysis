'''
Created on 2012-06-25

@author: rutje
'''
import numpy as np
from fetch.configuration import ranges

def findMinMax(data):    
    data.dtype.names
    return {h : {'min': np.min(data[h]), 'max':np.max(data[h])} for h in data.dtype.names}

def findNans(data, isClipTask):
    results = []
    nans = [h for h in data.dtype.names if np.isnan(np.sum(data[h]))]
    for n in nans:
        #clip apply #3 only J1, J2, LIN, Fg produce valid data,  (ignore ROT, ignore ThG)
        if not isClipTask or ('Rot' not in n and 'ThG' not in n):
            results.append(n)
    return results
        
def findDeadSensor(minmax, isClipTask):
    results = []
    
    for k, v in minmax.iteritems():
        if not isClipTask:
            if  (abs(v['max'] - v['min']) < 0.0001):
                results.append(k)
        else:
            if  (abs(v['max'] - v['min']) < 0.0001) and k != 'Rot_R' and k != 'ThG_R':
                results.append(k)
    return results

#TODO: change minmax range to handle different test types (needledrivers have different ThG)
def findOutOfRange(minmax):
    results = []
    for k, v in minmax.iteritems():
        r = ranges.get(k)
        if r and ((r['min'] is not None and (v['min'] < r['min'])) or 
                  (r['max'] is not None and (v['max'] > r['max']))):
            results.append(k)
    return results