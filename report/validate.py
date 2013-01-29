import numpy as np
import os, json

from fetch.configuration import ranges
from helpers import appendOrCreate

def findMinMax(data):    
    data.dtype.names
    return {h : {'min': np.min(data[h]), 'max':np.max(data[h])} for h in data.dtype.names}

def findNans(data, isClipTask):
    results = []
    nans = [h for h in data.dtype.names if np.isnan(np.sum(data[h]))]
    for n in nans:
        #clip apply #3 only J1, J2, LIN, Fg produce valid data,  (ignore ROT, ignore ThG)
        if not isClipTask or n not in ['Rot_R','ThG_R']: 
            results.append(n)
    return results
        
def findDeadSensor(minmax, isClipTask):
    results = []
    
    for k, v in minmax.iteritems():
        #appended 1/2/13 because left graspers not always closed during CA task
        #EDIT 1/28/13 now covered in ignoreErrors
        #if k == 'Fg_L' and isClipTask and (abs(v['max'] - v['min']) < 0.005): continue
        
        if not isClipTask:
            if  (abs(v['max'] - v['min']) < 0.005):
                results.append(k)
        else:
            if  (abs(v['max'] - v['min']) < 0.005) and k != 'Rot_R' and k != 'ThG_R':
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

##### Code to handle conditional error ignoring (IgnoreErrors) #####
def loadKnownErrors(filepath=None):
    '''Load the known error file regardless of being on local (windows) or
on ec2 (Unix). I hate backslashes! '''
    try:
        if filepath != None:
            fh = open(filepath,'r')
        elif "C:" in os.getcwd():
            fh = open(r'C:\Users\Tyler\.ipython\Simscore-Computing\report\KnownErrors.txt','r')
        else: fh = open('Simscore-Computing/report/KnownErrors.txt','r')
    except IOError: 
        print 'no KnownError file'
        return {}
        
    try:  
        ke = json.loads(fh.read())
    except ValueError:
        return {}
        
    fh.close()
    return ke
    
def evalKnownErrors(js, minmax, knownerrors):
    '''Given comuted info about an exam (js) and the minmax values and
a list of user-defined knownerrors, create a dict of sensors and failtype to ignore'''
    ignore= {}
    for tid in [js['LToolID'], js['RToolID']]:
        if tid in knownerrors.keys():
            snsr = knownerrors[tid][0]
            failtype = knownerrors[tid][1]
            #Implemented so that OutOfRanges could be direction specific
            if failtype == 'OutOfRange' and knownerrors[tid][2]=='min':
                if minmax[snsr][knownerrors[tid][2]] < ranges[snsr][knownerrors[tid][2]]: appendOrCreate(ignore, snsr, failtype)
            elif failtype == 'OutOfRange' and knownerrors[tid][2]=='max':
                if minmax[snsr][knownerrors[tid][2]] > ranges[snsr][knownerrors[tid][2]]: appendOrCreate(ignore, snsr, failtype)
                
            else: ignore[snsr] = [failtype]
    return ignore

def ignoreErrors(js, minmax, isClipApply):
    '''create dict of errors to ignore for simscore. include ignoring known errors
as well as specific, user-identified commonplace, non-important errors'''
    #Ignore known errors
    knownerrors = loadKnownErrors()
    ignore = evalKnownErrors(js, minmax, knownerrors)
    
    #Ignore dead FgL during ClipApply
    if isClipApply:
        appendOrCreate(ignore, 'Fg_L', 'DeadSensors')
        #Ignore really high Fg if ClipApply
        if minmax['Fg_R']['max'] > ranges['Fg_R']['max'] and minmax['Fg_R']['min'] > ranges['Fg_R']['min']:
            appendOrCreate(ignore, 'Fg_R', 'OutOfRange')
            
    #Ignore dead FgOffhand during Cutting
    if js["TaskType"] == 1:
        hand = 'L' if js["ProctorValues"]["LeftToolIsScissors"] else 'R'
        appendOrCreate(ignore, 'Fg_'+hand, 'DeadSensors')
    
    #DURING PRACTICE:
    #Ignore all Dead Fg
    if js['IsPractice']:
        appendOrCreate(ignore, 'Fg_L', 'DeadSensors')
        appendOrCreate(ignore, 'Fg_R', 'DeadSensors')
    return ignore
