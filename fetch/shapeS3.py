"""
######################

DEPRICATED FOR USE IN FUTURE COMPUTING, 
TLH, 12/6/2012

######################
"""

import numpy as np
import json
import fetchS3
import cStringIO
from operator import itemgetter
from collections import defaultdict, namedtuple
from datetime import datetime
from configuration import formats
from configuration import converterdict
from configuration import metafields, MetadatFieldNames
        
def getData(filename, bucketname="incoming-simscore-org", access=None, secret=None, is_secure=True): 
    conn = fetchS3.s3Connection(access, secret, is_secure) if access and secret else None
    txt, colNames = fetchS3.getFile(filename, bucketname, conn, is_secure=is_secure)
    meta = fetchS3.getMetaFile(filename[ :-3] + 'log', bucketname, conn)
    return dataParse(txt, colNames), meta

def getMetaData(filename, bucketname="incoming-simscore-org", access=None, secret=None, is_secure=True):
    conn =  fetchS3.s3Connection(access, secret, is_secure) if access and secret else None
    return fetchS3.getMetaFile(filename, bucketname, conn)

def getAllDataAfter(minfilename, bucketname="incoming-simscore-org", access=None, secret=None, is_secure=True):
    data = defaultdict(list)
    conn = fetchS3.s3Connection(access, secret, is_secure) if access and secret else None
    files = fetchS3.getFilesPastDate(minfilename, bucketname, conn)
    
    #Edit TLH 10.24.12 - cannot get max of empty file list, throws potentially terminating error 
    #Seems to be source of failure -- error: max() arg is an empty sequence*
    #maxfile = "edge1/2012/10/20.19.08.25.328.0"
    if files == []:
        maxfile = minfilename
    else:
        maxfile = max(files, key=itemgetter(1))[0][1] 
    
    #Parse takes in tuple of data for specific file, returns dict of EdgeUnitId, kinematics, filename, variables, etc.
    parse = lambda f: f[2] if f[0]=='meta' else json.dumps(dataParse(f[2][0], f[2][1]).tolist())
    for f in files:
        try:
            #f[0][1] is filename, f[0] is tuple of specific test info
            data[f[0][1]].append(parse(f[0]))
        except Exception as e:
            print 'shape.getAllDataAfter: ', e
            if f:
                print f[0], ':', f[1]
            else: print 'shape.getAllDataAfter: There is no file'
    return  maxfile, data

def exportData(minfilename=None, bucketname="incoming-simscore-org", access=None, secret=None, is_secure=True):
    meta = cStringIO.StringIO()
    data = cStringIO.StringIO()
    minfilename = "edge4/2012/07/01.23.59.53.109.3" if not minfilename else minfilename
    conn = fetchS3.s3Connection(access, secret, is_secure) if access and secret else None
    files = fetchS3.getFilesPastDate(minfilename, bucketname, conn)
    for fin in files:
        name = fin[0][1]
        dtype = fin[0][0]
        date = str(fin[1])
        if fin[0][0] == 'meta':
            parsed = metaParse(fin[0][2])
            joinedparsed = ','.join(str(p) for p in parsed[1])
            metaline = '{0},{1},{2},{3}'.format(name, dtype, date, joinedparsed)
            meta.write('%s\n' % metaline)
        elif fin[0][0] == 'data':
            for line in fin[0][2][0].readlines():
                data.write('{0},{1},{2}, {3}'.format(fin[0][1], fin[0][0], fin[1], line))
    return meta, data

def exportByMachine(machines, bucketname="incoming-simscore-org", access=None, secret=None, is_secure=True):
    meta = cStringIO.StringIO()
    data = cStringIO.StringIO()
    conn = fetchS3.s3Connection(access, secret, is_secure) if access and secret else None
    for machine in machines:
        files = fetchS3.getFilesByMachine(machine, bucketname, conn)
        for fin in files:
            name = fin[0][1]
            dtype = fin[0][0]
            date = str(fin[1])
            if fin[0][0] == 'meta':
                parsed = metaParse(fin[0][2])
                joinedparsed = ','.join(str(p) for p in parsed[1])
                metaline = '{0},{1},{2},{3}'.format(name, dtype, date, joinedparsed)
                meta.write('%s\n' % metaline)
            elif fin[0][0] == 'data':
                for line in fin[0][2][0].readlines():
                    dataline = ','.join(line.strip().split())
                    data.write('{0},{1},{2},{3}\n'.format(fin[0][1], fin[0][0], fin[1], dataline))
    return meta, data

def exportByUser(uids, bucketname="incoming-simscore-org", access=None, secret=None, is_secure=True):
    meta = cStringIO.StringIO()
    data = cStringIO.StringIO()
    conn = fetchS3.s3Connection(access, secret, is_secure) if access and secret else None
    files = fetchS3.getFilesByUser(uids, bucketname, conn, is_secure)
    for fin in files:
            name = fin[0][1]
            dtype = fin[0][0]
            date = str(fin[1])
            if fin[0][0] == 'meta':
                parsed = metaParse(fin[0][2])
                joinedparsed = ','.join(str(p) for p in parsed[1])
                metaline = '{0},{1},{2},{3}'.format(name, dtype, date, joinedparsed)
                meta.write('%s\n' % metaline)
            elif fin[0][0] == 'data':
                for line in fin[0][2][0].readlines()[1: ]:
                    if line.strip():
                        dataline = ','.join(line.strip().split())
                        data.write('{0},{1},{2},{3},{4}\n'.format(fin[0][1], fin[0][1].split('.')[-1], fin[0][0], fin[1], dataline))
    return meta, data
    

'''
Utilities
'''
def dataParse(f, names):
    try:
        dt = {'names' : names, 'formats' : formats}
        data = np.loadtxt(f, skiprows=1, comments='%',dtype=dt, converters=converterdict)
        return data
    except Exception as e:
        print 'shape.dataParse: ', e
        return e

def getFieldValues(fieldname, meta):
    line = []
    fields = MetadatFieldNames.get(fieldname, [])  
#    for field in fields:
             
    line = [meta.get(field, 'N/A') for field in fields]
    return line
        
        
def metaParse(meta):
    names = []
    metadata = []
    for f in metafields:
        x = meta.get(f, 'nan') 
        if type(x) is dict:
            n = ['%s_%s' %(f,k) for k in x.keys()]
            names.extend(n)
            metadata.extend(getFieldValues(f, x))
        else:
            names.append(f)
            metadata.append(x)
    return names, metadata
    
    
    