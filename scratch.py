# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import boto
import time, json
import boto.sqs.message

# <codecell>

conn = boto.connect_sqs(
        aws_access_key_id='AKIAJFD5VPO6RFKGTWIA',
        aws_secret_access_key='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')

# <codecell>

def process_queue(q, rs):
    
    #now do stuff to the message
    print json.loads(rs.get_body())["Subject"]
    print json.loads(rs.get_body())["Message"]
    #compute score
    #compute machine health
    time.sleep(2)
    
    #If successfull with processing, remove from queue:
    d = q.delete_message(rs)
    if d: print 'Deleted'
    
    #If still messages on SQS, keep processing
    #rs = q.read(wait_time_seconds=20)
    #if rs:
    #    process_queue(q, rs)
        
        
    
q = conn.get_queue('EdgeFiles2Process')
q.set_message_class(boto.sqs.message.RawMessage)

while True:
    
    rs = q.read(wait_time_seconds=20)
    if rs:
        process_queue(q,rs)
        
    time.sleep(1)
    

# <codecell>


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
file = open('2012.7.13_data_onwards', 'w')
# now let's pickle picklelist
pickle.dump(data,file)
# close the file, and your pickling is complete
file.close()

# <codecell>

diff_l_all = []
diff_r_all  = []

for k, v in data.iteritems():
    if len(v) > 1:
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

import matplotlib
fig = plt.figure()
n, bins, patches = hist(diff_r_all,50)

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


