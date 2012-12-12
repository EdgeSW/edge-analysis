# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import numpy as np
import pickle
import ast, json
import fetch.myS3 as myS3
import validity_metrics as vm

# <codecell>

minfilename = 'edge6/2012/7/13.21.07.03.288.0.txt'
mindate = myS3.getFileDateFromKey(minfilename)

data = myS3.getDataBetween(mindate=mindate, labeled=True, includeMeta=True, includePractice=False)

# <codecell>

file = open('data_past_7.13.2012', 'rb')
data = pickle.load(file)
file.close()


# <codecell>

n = 'edge2/2012/12/06.14.51.35.354.0.txt'
data[n]['data']

# <codecell>

drift = {}

for k, v in data.iteritems():
    
    #v= data.values()[0]
    #k = data.keys()[0]

    try:
        xx = v['data']
        ld = round(vm.start_v_end(xx['Lin_L']), 4)
        rd = round(vm.start_v_end(xx['Lin_R']), 4)
        
        if v['meta']['EdgeToolIdLeftHex'] in drift.keys():
            drift[v['meta']['EdgeToolIdLeftHex']].append([ld, k])
        else:
            drift[v['meta']['EdgeToolIdLeftHex']] = [[ld, k]]
            
        if v['meta']['EdgeToolIdRightHex'] in drift.keys():
            drift[v['meta']['EdgeToolIdRightHex']].append([rd, k])
        else:
            drift[v['meta']['EdgeToolIdRightHex']] = [[rd, k]]
          
    except:
        print 'bad data from:',k
        pass
print len(drift)

# <codecell>

for k, v in drift.iteritems():
    print k
    print len(v)
    for val in v:
        if abs(val[0]) > 1:
            print val

# <codecell>

import matplotlib
fig = plt.figure()
n, bins, patches = hist( ggg ,50)

# <codecell>


# now create a file
# replace filename with the file you want to create
file = open('2012.7.13_data_onwards.txt', 'wb')
# now let's pickle picklelist
pickle.dump(data,file)
# close the file, and your pickling is complete
file.close()

