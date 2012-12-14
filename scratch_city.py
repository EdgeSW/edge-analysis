# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>


# <codecell>

import time
f = open('/home/ubuntu/logs/lastchecks.log','w') 
f.write(str(int(time.time()))+'\n'+str(int(time.time())) )
f.close()

# <codecell>

f = open('/home/ubuntu/logs/lastchecks.log','r') 

int(f.readlines()[1].strip())

# <codecell>

import time
int(time.time())

# <codecell>


