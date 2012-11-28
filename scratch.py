# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from computing_imports import *
import fetch.shapeS3 as shape
import fetch.fetchS3 as fetchS3
import report.tools.validate as validate
import validity_metrics as vm
%load_ext autoreload
%autoreload
from boto.sqs.message import Message
conn = boto.connect_sqs(
        aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
        aws_secret_access_key='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')
import pprint
pp = pprint.PrettyPrinter(indent=4)

# <codecell>

filename = 'edge6/2012/11/13.21.07.03.288.0.txt'#'edge6/2012/10/24.21.59.05.325.0.txt'
bucketname = 'incoming-simscore-org'
is_secure = False if '.' in bucketname else True
data, meta = shape.getData(filename, bucketname, is_secure=is_secure)

# <codecell>

#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(meta)
#print data.dtype.names
jsonSimscore = vm.summary_metrics(meta, data, np.diff)
jsonSimscore = vm.data_metrics_append(jsonSimscore, data, filename)

# <codecell>

jsonSimscore

# <codecell>


# <headingcell level=1>

# SQS 

# <codecell>

q = conn.get_queue('EdgeFiles2Process')
q.set_message_class(boto.sqs.message.RawMessage)
rs = q.read()
print rs.get_body()

# <codecell>


# <codecell>

qq = conn.get_queue('myqueue')
from boto.sqs.message import Message

for i in range(1, 11):
   m = Message()
   m.set_body('This is message id %d.' %i)
   qq.write(m)


# <codecell>

from datetime import datetime
a= datetime.now()
time.sleep(0)
print 'heyo'
print datetime.now()-a

# <codecell>

minfilename = 'edge6/2012/7/13.21.07.03.288.0.txt'#'edge6/2012/10/24.21.59.05.325.0.txt'
bucketname = 'incoming-simscore-org'
is_secure = False if '.' in bucketname else True
maxfile, data = shape.getAllDataAfter(minfilename=minfilename, bucketname=bucketname, is_secure=is_secure)
import ast

# <codecell>

import pickle
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

print len(data)

# <codecell>

diff_x_all = []
diff_y_all  = []
diff_z_all  = []

for k, v in data.iteritems():
    if len(v) > 1:
        try:
            xx = np.array(ast.literal_eval(v[1]))
            x = xx[:,3]
            y = xx[:,6]
            z = xx[:,15]
            
            diff_x = (x[0]-x[-1])
            diff_y = (y[0]-y[-1])
            diff_z = (z[0]-z[-1])
            #if diff_l > 1 or diff_l<-1 or diff_r > 1 or diff_r < -1:
                #print k
                
            diff_x_all.append(diff_x)
            diff_y_all.append(diff_y)
            diff_z_all.append(diff_z)
        except:
            #print v[1]
            pass
            

# <codecell>

import matplotlib
fig = plt.figure()
n, bins, patches = hist(diff_x_all,50)

#TODO: check for linencdrift by ToolID

# <codecell>

v = data['edge6/2012/11/05.19.24.12.340.2']
try:
    xx = np.array(ast.literal_eval(v[1]))
    lin_l = xx[:,3]
    lin_r = xx[:,9]
    diff_l = (lin_l[0]-lin_l[-1])
    diff_r = (lin_r[0]-lin_r[-1])
    if diff_l > 1 or diff_l<-1 or diff_r > 1 or diff_r < -1:
        print k
        
    diff_l_all.append(diff_l)
    diff_r_all.append(diff_r)
except:
    #print v[1]
    pass

# <codecell>

print diff_l, diff_r

# <codecell>

print lin_l[0], lin_l[-1]
plot(lin_l[-100:])

# <codecell>


