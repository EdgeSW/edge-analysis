'''
Created on 2012-06-25

@author: rutje
'''
import fetch.shapeS3 as shape
import validate
from fetch.configuration import dtype, rating, toolRight, toolLeft 
from collections import defaultdict
import json
import numpy as np



def getIndices(v):
    meta = 0 if v[0].get(toolRight) else 1
    return {'meta' : meta, 'data' : 1 - meta }

def validateData(d):
    fails = defaultdict(lambda: defaultdict())
    for k, v in d.iteritems():
        if len(v) == 2:
            indices = getIndices(v)
            try:
                idR = v[indices['meta']].get(toolRight)
                idL = v[indices['meta']].get(toolLeft)

                data = np.fromiter(v[indices['data']], dtype)
                minmax = validate.findMinMax(data)
                dse = validate.findDeadSensor(minmax)
                oor = validate.findOutOfRange(minmax)
                isClipTask = k[-1] == 3
                nan = validate.findNans(data, isClipTask)
                if dse or oor or nan:
                    txt = '%s.txt' % k
                    fails[txt]['deadSensor'] = rating(dse)
                    fails[txt]['oor'] = rating(oor)
                    fails[txt]['nan'] = rating(nan)
                    fails[txt]['toolIds'] = [idL, idR]
            except Exception as e:
                print 'calibration.validateData', k, ': ' ,e
    return fails
            
            
                
              
              
            
        
    
     


 







