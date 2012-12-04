# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

minfilename = 'edge6/2012/7/13.21.07.03.288.0.txt'#'edge6/2012/10/24.21.59.05.325.0.txt'
bucketname = 'incoming-simscore-org'
is_secure = False if '.' in bucketname else True
maxfile, data = shape.getAllDataAfter(minfilename=minfilename, bucketname=bucketname, is_secure=is_secure)

# <codecell>

# now create a file
# replace filename with the file you want to create
file = open('2012.7.13_data_onwards.txt', 'wb')
# now let's pickle picklelist
pickle.dump(data,file)
# close the file, and your pickling is complete
file.close()

# <codecell>

file = open('2012.7.13_data_onwards.txt', 'rb')
data = pickle.load(file)
file.close()

# <codecell>

import sys, os
sys.path.append('C:\\Users\\Tyler\\.ipython\\Simscore-Computing')

import ast
import pickle
import numpy as np
import validity_metrics as vm
drift = {}

for k, v in data.iteritems():

    #v= data.values()[4]
    
    if len(v)>1:
        try:
            xx = np.array(ast.literal_eval(v[1]))
            #item 3 is Lin_L, item 9 is Lin_R
            ld = round(vm.start_v_end(xx[:,3]), 4)
            rd = round(vm.start_v_end(xx[:,9]), 4)
            
            if v[0]['EdgeToolIdLeftHex'] in drift.keys():
                drift[v[0]['EdgeToolIdLeftHex']].append([ld, k])
            else:
                drift[v[0]['EdgeToolIdLeftHex']] = [[ld, k]]
                
            if v[0]['EdgeToolIdRightHex'] in drift.keys():
                drift[v[0]['EdgeToolIdRightHex']].append([rd, k])
            else:
                drift[v[0]['EdgeToolIdRightHex']] = [[rd, k]]
              
        except:
            #print 'bad data from:',k
            pass
        

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

