# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import numpy as np
import json, string, re
import time, datetime
import report.validate as validate
import pprint
import boto
import ast
import pickle
import math

# <headingcell level=4>

# Test Summary Metrics

# <codecell>

ok = 'clear'
bad = 'error'

def round_float(f,decimals):
    if isinstance(f, float):
        return round(f,decimals)
    else: return f
    
def round_dict(d,decimal):
    '''round any float values in a dictionary to # decimal places.
Will only round floats that are values of keys, not contained in lists/tuples.'''
    
    for key, v in d.iteritems():
        if isinstance(v, float):
            d[key] = round(v,decimal)
            
        elif isinstance(v, dict):
            d[key] = round_dict(v, decimal)
         
    return d  

def nan_replace(d):
    '''replace all np.nan with string "NaN" for usage '''
    if isinstance(d, dict):
        for k,v in d.iteritems():
            if type(v) not in [list, dict, tuple]: 
                try: d[k] = 'NaN' if np.isnan(v) else v
                except: d[k] = v
            else: d[k] = nan_replace(v)
    elif isinstance(d, list):
        for i in range(len(d)):
            if type(d[i]) not in [list, dict, tuple]:  
                try: d[i] = 'NaN' if np.isnan(d[i]) else d[i]
                except: d[i] = d[i] #need this?
            else: d[i] = nan_replace(d[i])
    elif isinstance(d, tuple):
        copy = ()
        for item in d:
            if type(item) not in [list, dict,tuple]: 
                try: copy = copy + ('NaN',) if np.isnan(item) else copy +(item,)
                except: copy = copy + (item,)
            else: copy = copy + (nan_replace(item),) 
        d = copy
            
    return d


def start_v_end(*args):
    '''returns tuple of start-end values for each array given to function,
returns float if one array provided'''
    if len(args)>1:
        return tuple( e[-1]-e[0] for e in args)
    else: return args[0][-1]-args[0][0]

# <codecell>

def summary_metrics(meta,data,conn):
    jsonSimscore = {
                    
        #TestID    Int    The uniquely generated ID for this test score to associate all other data with.
        'TestID' : meta['DataFileNameOnS3'][:-4] 
        #TaskType    String    Task Type.
        ,'TaskType' : int(meta['DataFileNameOnS3'].split('.')[-2])
        #IsPractice    Boolean    Is this a scored test?
        ,'IsPractice' : meta["IsPracticeTest"]
        #MetadataFilename    String    Metadata Filename and location in S3.
        ,'MetadataFilename' : meta["MetaDataFileNameOnS3"]    
        #TestDataFilename    String    Test Data Filename and location in S3.
        ,'TestDataFilename' : meta['DataFileNameOnS3']    
        #VideoDataFilename    String    Video Data Filename and location in S3.
        ,'VideoDataFilename' : meta["VideoFileNameOnS3"]
        #UserID    String    User ID.
        ,'UserID' : meta['DataFileNameOnS3'].split('.')[-3] if int(meta['UserId']) == 0 else str(meta['UserId']) 
        #ProctorID    String    Proctor ID.
        ,'ProctorID' : str(meta["ProctorId"])
        #EdgeID    String    EDGE ID.
        ,'EdgeID' : str(meta["EdgeUnitId"])
        #SwVersion    String    EDGE software version.
        ,'SwVersion' : meta["EdgeSoftwareVersion"]
        #RToolID    String    Right Tool ID.
        ,'LToolID' : meta.get('EdgeToolIdLeftHex',meta['EdgeToolIdLeft']) #return hex ID if available (old tests do not report hex)
        ,'RToolID' : meta.get('EdgeToolIdRightHex',meta['EdgeToolIdRight'])
        #TestLength    String    The length of time it took to complete the task. Ex: 02:00.0.
        ,'TestLength' : meta["TestDurationInSeconds"]
        #testlengthCheck	Boolean	Length of test is within acceptable bounds
        ,'TestLengthCheck': ok if float(meta["TestDurationInSeconds"])>5 else bad
        #Badframe	Int	Video dropped frame count.
        ,'BadFramesCount': meta['VideoDroppedFrameCount']
        #BadFramesCheck bool        serious amount of dropped frames
        ,'BadFrames': ok if meta['VideoDroppedFrameCount'] < 30 else bad
        #IsUpdate   Bool   Set to False for all first time tests. must manually set to true to update Simscore's entry for this test
        ,'IsUpdate': True
                    }

    #ProctorValues
    tasks = ['PegTransfer','Cutting','Suture','ClipApply']
    try: TaskType = tasks[jsonSimscore['TaskType']]
    except: TaskType = 'Unknown'
    jsonSimscore['ProctorValues'] = meta.get('Proctor'+TaskType,'Unknown')
    
    #proctor	Boolean	Sanity check on proctor field values
    fields = ["NumberDropped", "DistanceFromTargetDot","DistanceFromTargetDotLeft","DistanceFromTargetDotRight","NumberOfTimesOutsideTheLine"]
    m = ok
    if TaskType != 'Unknown':
        for field in fields:
            val = meta['Proctor'+TaskType].get(field, 0)
            if not isinstance(val, int) or val< 0 or val > 25:
                m = bad
        jsonSimscore['ProctorValuesCheck'] = m
    else: jsonSimscore['ProctorValuesCheck'] = 'Unknown'
    
    #UploadDate    String    Upload Date
    xx = re.findall(r'[0-9]+', str(meta['DataFileNameOnS3']))
    jsonSimscore['UploadDate'] = '-'.join(xx[1:4])+' '+':'.join(xx[4:7])
    
    #UploadDateUnix    Time    Date converted into Unix Epoch C Time for fast sorting.
    filename = re.findall(r'[0-9]+', str(meta['DataFileNameOnS3']))
    edgetime = '.'.join(filename[1:7])
    jsonSimscore['UploadDateUnix'] = int(time.mktime(time.strptime(edgetime, '%Y.%m.%d.%H.%M.%S'))) 
    
    #continuous	Boolean	Check for any temporal discontinuities 
    check = ok
    for x in np.diff(np.diff(data['%Time_V1']) ):
        if abs(x) > 0.05: check = bad
    jsonSimscore['Continuous'] = check
    
    #VideoFileExists    Bool     Checks to see if the video file is on S3 at above location
    if not meta["IsPracticeTest"]:
        jsonSimscore['VideoFileExists'] = ok if conn.get_bucket('video-simscore-org').get_key(meta["VideoFileNameOnS3"]) else bad    
    else: jsonSimscore['VideoFileExists'] = ok
        
        
    return jsonSimscore

#jsonSimscore = summary_metrics(meta,data,diff)
#pp.pprint(jsonSimscore)

# <headingcell level=4>

# Test Data Metrics

# <codecell>

from report.configuration import isClipTask   
                
def data_metrics_append(jsonSimscore, data, filename):
    minmax = validate.findMinMax(data)
    isClipApply = isClipTask(filename)
    
    jsonSimscore.update({
        #Dead	Boolean	
        'DeadSensors' : validate.findDeadSensors(data, minmax, jsonSimscore['TaskType'], jsonSimscore['IsPractice'])
        #Out of Range	Boolean
        ,'OutOfRange' : validate.findOutOfRanges(minmax, jsonSimscore['TaskType'])
        #NaN	Boolean	
        ,'NaNSensors' : validate.findNans(data, isClipApply)  
        #Known errors to ignore on simscore.org
        ,'IgnoreErrors' : validate.ignoreErrors(jsonSimscore, minmax, isClipApply)
        #Max    Float    Min    Float                 
        ,'MinMax' : nan_replace(minmax)
    })
    return jsonSimscore

#jsonSimscore = data_metrics_append(jsonSimscore, data, filename)
#pp.pprint(jsonSimscore)

# <headingcell level=4>

# Machine Health Metrics

# <codecell>

def machine_health_append(jsonSimscore, meta, data):    

    #	kinematicsCheck	Boolean	Kinematics set to default values
    
    
    #	ToolTipDriftValue	Float	
    jsonSimscore['ToolTipDriftValue'] = {'left':{'x': start_v_end(data['X_L']), 'y':start_v_end(data['Y_L']), 'z':start_v_end(data['Z_L'])}
                                        ,'right': {'x':start_v_end(data['X_R']), 'y':start_v_end(data['Y_R']), 'z':start_v_end(data['Z_R'])} } 
    
    #	ToolTipDrift	Boolean	Tool tip position same at beginning and end of test (tooltip drift)
    vall = ok; valr = ok
    for v in list(start_v_end(data['X_L'],data['Y_L'],data['Z_L'])):
        if v > 3: vall = bad
    for v in list(start_v_end(data['X_R'],data['Y_R'],data['Z_R'])):        
        if v > 3: valr = bad
    jsonSimscore['ToolTipDrift'] = {'left':vall, 'right':valr}
    
    #	LinEncDrift	Boolean	Is there linear encoder drift?
    jsonSimscore['LinEncDrift'] = {'left': bad if abs(start_v_end(data['Lin_L'])) > 2 else ok, 'right': bad if abs(start_v_end(data['Lin_R'])) > 2 else ok}
    #	LinEncDriftValue	Float	Offset from start and finish linear encoder point
    jsonSimscore['LinEncDriftValue'] = {'left': start_v_end(data['Lin_L']), 'right': start_v_end(data['Lin_R'])}
    #	InvalidToolID	Boolean	Check that tool IDs exist in database
    
    #	lastCalibration	String	Date of last machine calibration.
    temp = meta['CalibrationData']['CalibrationSavedDate'].split('T')
    jsonSimscore['LastCalibration'] = str(temp[0]+' '+temp[1])
    
    #FailType	List of String	List of Failure Types for whole test: OB Data, Video Corruption
    possible_errors = ['NaNSensors','DeadSensors','OutOfRange','LinEncDrift','ToolTipDrift','BadFrames','Continuous','ProctorValuesCheck','TestLengthCheck']
    failtypes = []
    for error in possible_errors:
        if error == 'LinEncDrift' or error == 'ToolTipDrift':
            if jsonSimscore[error]['left'] != ok or jsonSimscore[error]['right'] != ok : failtypes.append(error) 
        elif error in ['NaNSensors','DeadSensors','OutOfRange']:
            if jsonSimscore[error] != [] : failtypes.append(error)
        elif jsonSimscore[error] != ok : failtypes.append(error)
            
    jsonSimscore['FailTypes'] = failtypes
    
    return jsonSimscore

#jsonSimscore = machine_health_append(jsonSimscore, data)

