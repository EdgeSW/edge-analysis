# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np

# <codecell>

def fix_offset(npdata, offset=1e8):    
    '''cleans up data with large, instantaneous offsets (intended for Rot)'''
    ndata = np.copy(npdata -npdata[0])
    diffs = np.diff(ndata)
    idxs = np.nonzero(abs(diffs) > offset)
    
    for idx in idxs[0]:
        ndata[idx+1:] = ndata[idx+1:] - diffs[idx]
        
    return ndata

# <codecell>


