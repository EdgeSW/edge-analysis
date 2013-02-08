# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#%load_ext autoreload
#%autoreload 2
import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')
from scipy.cluster import vq
import numpy as np
import json
from collections import defaultdict, namedtuple
from operator import itemgetter
import cStringIO
import scipy
from scipy.signal import butter, filtfilt

import HMM.myBigQuery as myBQ
from HMM.myBigQuery import getBody
from HMM.myBigQuery import httpGoogle
from HMM.myBigQuery import getSchemaFields

from HMM.myBigQuery import loadTableFromCSV
from HMM.myBigQuery import queryTableData
from HMM.myBigQuery import queryGoogle

from datetime import datetime

# <codecell>

def create_codebook(args):
    features, size, i = args
    
    import scipy.cluster as cluster
    #left = c.vq.kmeans(features[0], size)
    #right = c.vq.kmeans(features[1], size)
    #return (left, right)
    cdbk = cluster.vq.kmeans(features, size)
    return cdbk

# <codecell>

def getFeatures(table_name, sensors=None, task=None, hand=None, order=None, limit=0, keys=None, asdict=False):
    '''Query BQ for data from table_name based on SQL query entries given above. can return as dict or 
tuple of keys, array of values. 
- if limit is <=0, will return all. otherwise will limit to limit. 
- Order needs to be formatted as the second part of SQL ORDER BY query.'''
    #sensors = sensors if sensors else getSensors(table_name)

    sensorquery = qSensors(table_name, sensors, task, hand, keys, order, limit)
    print sensorquery
    results = queryGoogle(sensorquery)
    
    if asdict: #Return data as {key:np array, key:np.array ...}
        hugedict={}
        for row in results['rows']:
            #If this ID is not a key in the dict, add it
            if row['f'][0]['v'] not in hugedict.keys(): hugedict[row['f'][0]['v']] = []
            #Regardless, append these values to that list   
            hugedict[row['f'][0]['v']].append( [float(vals['v']) for vals in row['f'][1:] ])
            
        for k, v in hugedict.iteritems():
            hugedict[k] = np.array(v)#better/faster way?
            
        return hugedict
        
    else: #return tuple of [key, key...], [mxn raw data]
        ids = [] #to hold the id corresponding to each timepoint
        values = [] #to hold the raw data
        for row in results['rows']:
            ids.append(row['f'][0]['v'])
            values.append([float(vals['v']) for vals in row['f'][1:] ])
                
        return np.array(ids), np.array(values)


# <codecell>

def qSensors(table_name, sensors=None, task=None, hand=None, keys=None, order=None, limit=0):
    '''Format a SQL querey to BigQuery based on info about table'''
    sensors = sensors if sensors else getSensors(table_name) 

    SELECT = "SELECT key, "+(', '.join( [sensor for sensor in sensors] ))
    
    FROM = (" FROM [data."+ table_name +"] ")
    
    wh = []
    if task: wh.append("task='%s' "%task)
    if hand: wh.append("hand='%s' "%hand)
    wh = 'AND '.join(wh)
    WHERE = "WHERE "+ wh if wh else ''
    
    if keys: WHERE = WHERE + "AND (key='"+"' OR key='".join(keys)+ "') "
    
    ORDER = " ORDER BY "+str(order) if order else ''
    LIMIT = " LIMIT "+str(int(limit)) if limit>0 else ''
    
    return SELECT + FROM + WHERE + ORDER + LIMIT

#sensors = ['QgL', 'FgL', 'QgR', 'FgR']
#print qSensors('timdata', sensors=['QgL','FgL'], hand='left', task='suturing', limit=1000, keys=['pegtransfer_1','pegtransfer_2','pegtransfer_3'], order='key, Time')

# <codecell>

def upload_features(features, date, dataset, hand=None, task=None, tablename=None):
    data = cStringIO.StringIO()
    fields = myBQ.getSchemaFields(tablename)
    for k, v in features.iteritems():
        for row in v:
            data.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}\n'.format(k, row[0], 
                    row[1], row[2], row[3], row[4], row[5], row[6], row[7], date, dataset, hand, task))
                       
    body = myBQ.getBody(data.getvalue(), fields, tablename, 'data'
                            , createDisposition='CREATE_IF_NEEDED'
                            , writeDisposition='WRITE_APPEND')
    myBQ.loadTableFromCSV(body)
    
    

# <codecell>

def upload_codebook(left, right, dataset, cdbkfeat, task, distL, distR):
    data = cStringIO.StringIO()
    fields = myBQ.getSchemaFields('codebooks')  
    #dataset, date, hand, task, features, distortion, jsoncdbk
    data.write('{0},{1},{2},{3},{4},{5},"{6}"\n'.format(dataset, '10-OCT-2012 1:33', 'left',  task, cdbkfeat, distL, json.dumps(left[0].tolist())))   
    data.write('{0},{1},{2},{3},{4},{5},"{6}"\n'.format(dataset, '10-OCT-2012 1:33', 'right', task, cdbkfeat, distR, json.dumps(right[0].tolist())))

    body = myBQ.getBody(data.getvalue(), fields, 'codebooks', 'data'
                              , createDisposition='CREATE_IF_NEEDED'
                              , writeDisposition='WRITE_APPEND')
    myBQ.loadTableFromCSV(body)
    
#upload_codebook(min(results[0], key=itemgetter(1)), min(results[1], key=itemgetter(1)))
#upload_codebook(cdbkL,cdbkR, dataset, cdbkfeat, task, 0.0401127109316, 0.0396742994943)

# <codecell>

#download codebook from bigquery
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

#cdbkL, cdbkR, dataset, task = download_codebook('10-OCT-2012 1:33')

# <codecell>

def size_codebook(task):
    if task in ['cutting']: return 67
    if task in ['suturing']: return 70
    if task in ['pegtransfer']: return 57
    return 70

# <codecell>

def codebookApply(features, codebook):
    '''
    returns the code and distance for the codebook
    '''
    return vq.vq(features, codebook)

# <codecell>

def floats(s):
    try:
        return float(s)
    except Exception as e:
        return s
        #print 'error :', e
        #return np.NaN

# <codecell>

def getSensors(table_name):
    fields = json.loads(getSchemaFields(table_name))
    sensors =  [field['name'] for field in fields][4:]
    return sensors

#print getSensors('timdata')

# <codecell>

def getTasks(table_name):
    tasks = queryGoogle("SELECT task from data.{0} GROUP BY task".format(table_name))
    return [task['f'][0]['v'] for task in tasks['rows']]

#print getTasks('timdata')

# <markdowncell>

# #Utilities

# <headingcell level=1>

# Legacy Code from the Ancient Times

# <markdowncell>

# ##query to get Quantiles

# <codecell>

    
def qQuantiles(sensor, table_name, task): 
    return "SELECT QUANTILES({0}, 1000) as q{0} FROM [data.{1}] WHERE task=='{2}'".format(sensor, table_name, task)
z='''
left = ['QgL', 'FgL']
right = ['QgR', 'FgR'] 
sensors = ['QgL', 'FgL', 'QgR', 'FgR']
d =  {sensor: queryGoogle(qQuantiles(sensor, 'timdata', 'suturing')) for sensor in sensors}
print d
'''

# <codecell>

def qThresholdSchema(task, table_name):
    sensors = getSensors(table_name)
    fields = ', '.join(sensors)
    return "SELECT threshold, task, {0} FROM data.schemata WHERE task=='{1}' AND table_name=='{2}'".format(fields, task, table_name)

# <codecell>

def getThresholds(table_name, dataset=None, task_type=None):
    dataset = dataset if dataset else table_name

    thresholds = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    #data = queryTableData('data', 'thresholds')
    qs = "SELECT task, table_name, threshold, sensor_name, sensor_value FROM data.thresholds WHERE table_name='{0}'".format(dataset)
    data = queryGoogle(qs)
    for row in data['rows']:
        cells = row['f']
        task = 'pegtransfer' if cells[0]['v']=='PegTx' else cells[0]['v'].lower()
        ttype = cells[2]['v']
        sensor = cells[3]['v']
        thresholds[task][sensor][ttype] = cells[4]['v']
    
    if task_type:
        return thresholds.get(task_type, 'ERROR: task not found')
    
    return thresholds


#print getThresholds('timdata')

# <codecell>

def createThresholdsTable(table_name):
    data = createThresholds(table_name)
    fields = getSchemaFields('thresholds')       
    body = getBody(data.getvalue(), fields, 'thresholds', 'data'
                               , createDisposition='CREATE_IF_NEEDED'
                               , writeDisposition='WRITE_APPEND')
    loadTableFromCSV(body)
#createThresholdsTable('timdata')

# <codecell>

def createThresholds(table_name):
    sensors = getSensors(table_name)
    thresholds = cStringIO.StringIO()
    for task in getTasks(table_name):
        #create dict of sensor: quantiles binned into 1000 bins
        quantiles = {sensor: queryGoogle(qQuantiles(sensor, table_name, task)) for sensor in sensors}
        for field in permil._fields: #permil._fields is essentially a dict of threshold names and bin value
            p = getattr(permil, field) #p is going to be one of (4, 19 979 994)
            for sensor in sensors:
                thresholds.write('{0},{1},{2},{3},{4}\n'.format(task, table_name, field, sensor, quantiles[sensor]['rows'][p]['f'][0]['v']))
        #thresholds = cStringIO.StringIO(open('thresholds.csv').read()) #to hardcode thresholds from matlab
    return thresholds

#print createThresholds('timdataMatlab').getvalue()

# <markdowncell>

# ##query to remove outliers based on thresholds

# <codecell>

quantiles = namedtuple('quantiles', 'lowOutlier lowNorm highNorm highOutlier')
permil = quantiles(4, 19, 979, 994)

# <codecell>

def qOutliers(task, table_name, thresholds=None, limit=0, sensors=None):
    sensors = sensors if sensors else getSensors(table_name) 
    SELECT = ("SELECT key, ")   
    select = [] 
    FROM = (" FROM [data."+ table_name +"] ")
    WHERE = ("WHERE task='{0}' AND ".format(task))
    LIMIT = " LIMIT "+str(int(limit))
    where = []
    for sensor in sensors:
        select.append(sensor)
        if abs(float(thresholds[task][sensor]['lowNorm']) - float(thresholds[task][sensor]['highNorm'])) > 0.01 or \
           abs(float(thresholds[task][sensor]['lowOutlier']) - float(thresholds[task][sensor]['highOutlier'])) > 0.01:
            where.append("({0} > {1} AND {0} < {2})\n".format(sensor, thresholds[task][sensor]['lowOutlier'], thresholds[task][sensor]['highOutlier']))
    #if limit  > 0:  return SELECT + (', '.join(select)) + FROM + WHERE + ' AND '.join(where) + LIMIT
    return SELECT + (', '.join(select)) + FROM + WHERE + ' AND '.join(where) + (LIMIT if limit > 0 else '')


#sensors = ['QgL', 'FgL', 'QgR', 'FgR']
#print qOutliers('suturing', 'timdata', getThresholds('timdata', 'timdataMatlab'), sensors)

# <codecell>

'''
def getFeaturesOld(table_name, task, limit, dataset=None, sensors=None):

    sensors = sensors if sensors else getSensors(table_name)
    dataset = dataset if dataset else table_name
    print 'table_name=', table_name, ' task=',task, ' dataset=', dataset, ' sensors=', sensors
    thresholds = {task: getThresholds(table_name, dataset, task)}
    outliers = qOutliers(task, table_name, thresholds, limit, sensors)
    results = queryGoogle(sensorquery)

    return (np.array([[floats(field['v']) for field in row['f']] for row in results['rows']]), thresholds[task])
'''

