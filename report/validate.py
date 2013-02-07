import numpy as np
import os, json

from report.configuration import ranges
from report.configuration import task_ranges
from helpers import appendOrCreate
from report.KnownErrors import knownerrors

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

#TODO: change minmax range to handle different test types (needledrivers have different ThG)
def oldFindOutOfRange(minmax):
    results = []
    for k, v in minmax.iteritems():
        r = ranges.get(k)
        if r and ((r['min'] is not None and (v['min'] < r['min'])) or 
                  (r['max'] is not None and (v['max'] > r['max']))):
            results.append(k)
    return results
    
def findOutOfRanges(minmax, taskid):
    results = []
    for snsr, v in minmax.iteritems():
        r = task_ranges[taskid][snsr]
        if r and ((r['min'] is not None and (v['min'] < r['min'])) or 
                  (r['max'] is not None and (v['max'] > r['max']))):
            results.append(snsr)
    return results

############Dead Sensor Checks###############
def isDead(vector, dmin, dmax, taskid, snsr, isPractice):
    '''Vector: one senor vector. dmin and dmax are calculated from report.validate.
isClipApply is a boolean value.
Function returns boolean.'''
    #first, do a check to make sure Rotation isn't off the charts
    if dmin < -1e6 or dmax > 1e6: return False
    
    #first check - highly stringent, whole test approach
    if abs(dmax - dmin) < 0.005: 
        return True
    
    if isPractice: return False
    
    #second check - does any pair of precise values account for 95% of values
        #and those two values are separated by less than 1 unit
    numbins = (dmax - dmin)/0.01
    if numbins > 720/0.01: numbins = 720/0.01
    a, b = np.histogram(vector, numbins)
    
    if sum(a[a.argsort()[-2:]])/float(len(vector)) > .95:
        return True
    
    #placed so that the third check is not performed for clip applys and
    #that suturing tasks don't do a length check for grasps (normal usage)
    if taskid == 3: return False
    if taskid == 2 and snsr in ['ThG_L','ThG_R']: return False
    
    #third check - is data dead for a time
    deadtime = 25*30#seconds*samplerate
    timeAtEndToAvoid = 60*30 if taskid==2 else 0 #since users set down tool to cut
    for i in range(0,len(vector)-deadtime-timeAtEndToAvoid, 5*30):
        if np.max(vector[i:i+deadtime]) - np.min(vector[i:i+deadtime]) < 0.01:
            return True
        
    return False
    
def isFgDead(Fg, dmin, dmax):
    '''The more complex checks in isDead do not apply to grasp force, which is often
intentionally "dead" for extended periods between grasps. Thus, a very simple check is required'''
    if dmax-dmin < 1: #3 is Tim's cutoff for grasp
        return True
    else:
        return False

def findDeadSensors(data, minmax, taskid, isPractice):
    '''overarching check for dead sensors in a given test. data is a matrix of sensor 
vectors, minmax is a dict of dicts computed from validate.minmax.
Returns: a list of sensors determined to be dead.'''
    results = []
    
    for name in data.dtype.names:
        if taskid ==3 and name in ['Rot_R','ThG_R']:
            continue
        
        if name in ['Fg_L','Fg_R']:
            if isFgDead(data[name], minmax[name]['min'], minmax[name]['max']):
                results.append(name)
        elif isDead(data[name], minmax[name]['min'], minmax[name]['max'], taskid, name, isPractice):
            results.append(name)
            
    return results

def oldFindDeadSensor(minmax, isClipTask):
    results = []
    for k, v in minmax.iteritems():
        if not isClipTask:
            if  (abs(v['max'] - v['min']) < 0.005):
                results.append(k)
        else:
            if  (abs(v['max'] - v['min']) < 0.005) and k != 'Rot_R' and k != 'ThG_R':
                results.append(k)
    return results

######## Code to handle conditional error ignoring (IgnoreErrors) ########
def evalKnownErrors(js, minmax, knownerrors):
    '''Given comuted info about an exam (js) and the minmax values and
a list of user-defined knownerrors, create a dict of sensors and failtype to ignore'''
    ignore= {}
    for tid in [js['LToolID'], js['RToolID']]:
        if tid in knownerrors.keys():
            snsr = knownerrors[tid][0]
            failtype = knownerrors[tid][1]
            minormax = minmax[snsr][knownerrors[tid][2]]
            #Implemented so that OutOfRanges could be direction specific
            if failtype == 'OutOfRange' and knownerrors[tid][2]=='min':
                if minormax > knownerrors[tid][3] and minormax < task_ranges[js['TaskType']][snsr]['min']: 
                    appendOrCreate(ignore, snsr, failtype)
            elif failtype == 'OutOfRange' and knownerrors[tid][2]=='max':
                if minormax < knownerrors[tid][3] and minormax > task_ranges[js['TaskType']][snsr]['max']: 
                    appendOrCreate(ignore, snsr, failtype)
                
            else: ignore[snsr] = [failtype]
    return ignore

def ignoreErrors(js, minmax, isClipApply):
    '''create dict of errors to ignore for simscore. include ignoring known errors
as well as specific, user-identified commonplace, non-important errors'''
    #Ignore known errors
    ignore = evalKnownErrors(js, minmax, knownerrors)
    
    #Ignore dead FgL during ClipApply
    if isClipApply:
        appendOrCreate(ignore, 'Fg_L', 'DeadSensors')
        #Ignore really high Fg if ClipApply
        if minmax['Fg_R']['max'] > ranges['Fg_R']['max'] and minmax['Fg_R']['min'] > ranges['Fg_R']['min']:
            appendOrCreate(ignore, 'Fg_R', 'OutOfRange')
            
    #Ignore dead FgOffhand during Cutting
    if js["TaskType"] == 1:
        hand = 'R' if js["ProctorValues"]["LeftToolIsScissors"] else 'L'
        appendOrCreate(ignore, 'Fg_'+hand, 'DeadSensors')
    
    #DURING PRACTICE:
    #Ignore all Dead Fg
    if js['IsPractice']:
        appendOrCreate(ignore, 'Fg_L', 'DeadSensors')
        appendOrCreate(ignore, 'Fg_R', 'DeadSensors')
    return ignore
