# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import scipy
#from scipy.signal import butter, filtfilt

# <codecell>

def fixOffset(npdata, offset=1e8):    
    '''cleans up data with large, instantaneous offsets (intended for Rot)'''
    ndata = np.copy(npdata -npdata[0])
    diffs = np.diff(ndata)
    idxs = np.nonzero(abs(diffs) > offset)
    
    for idx in idxs[0]:
        ndata[idx+1:] = ndata[idx+1:] - diffs[idx]
        
    return ndata

# <codecell>

def arcLength(d, th):
    '''d = 3xn data (x, y, z) converted to arc length.
Movement below th cut to zero, data should be filtered prior'''
    pass

# <codecell>

def fb(data, i, howfar):
    return (data(i+howfar)-data(i-howfar))

def holo(f, h):
    '''Calculate time derivative according to holoborodko's 11th order method
http://www.holoborodko.com/pavel/numerical-methods/numerical-derivative/smooth-low-noise-differentiators/
f = the data to be differentiated
h = the step size, or change in time, between each sample'''
    
    df = np.zeros(len(f)) 
    
    for i in range(len(f)):
        #Real 11th order Holoborodko
        if i >=5 and i <= len(f)-6:
            df[i] = (322*(f[i+1]-f[i-1])+256*(f[i+2]-f[i-2])+39*(f[i+3]-f[i-3])
                -32*(f[i+4]-f[i-4])-11*(f[i+5]-f[i-5]) ) / (1536*h)
            
        #Deal with head/tail cases
        elif i == 0: df[i] = (f[i+1]-f[i]) / h
        elif i == len(f)-1: df[i] = (f[i]-f[i-1]) / h 
        elif i == 1 or i == len(f)-2:
            df[i] = (f[i+1]-f[i-1])/(2*h)  
        elif i == 2 or i == len(f)-3:
            df[i] = (2*(f[i+1]-f[i-1])+f[i+2]-f[i-2])/(8*h)  
        elif i == 3 or i == len(f)-4:
            df[i] = (39*(f[i+1]-f[i-1])+12*(f[i+2]-f[i-2])-5*(f[i+3]-f[i-3])) / (96*h)      
        elif i == 4 or i == len(f)-5:
            df[i] = (27*(f[i+1]-f[i-1])+16*(f[i+2]-f[i-2])-(f[i+3]-f[i-3])-2*(f[i+4]-f[i-4])) / (96*h)
            
    return df

# <codecell>

def butterLowpass(input_sig=None, N=10, Wn=5, Fs=None, filter_saftey_margin=1.15):
    '''N = filter order, Wn is cutoff frequency, Fs is sampling frequency, 
safety_marign multiplies cutoff frequency to prevent data wipeout'''
    b, a = scipy.signal.iirfilter(N, filter_saftey_margin*Wn/(Fs/2), btype='low', ftype='butter')
    return scipy.signal.filtfilt(b, a, input_sig)

# <codecell>

def dRtaArctan(dRta):
    '''(kpi/2)arctan(pi*dQ3/k) where k = 125deg*sec. See Timk Thesis p32'''
    k = 125
    return (k*np.pi/2) * np.arctan(np.pi*dRta/k)

