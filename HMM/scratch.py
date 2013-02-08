# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext autoreload
%autoreload 2

# <codecell>

import sys
sys.path.append('C:\\Users\\Tyler\\.ipython\\edge-analysis')
from scipy.cluster import vq
import numpy as np
import json, copy
import scipy
import nltk

from datetime import datetime
import matplotlib.pyplot as plt
import scipy.cluster as cluster
from HMM.data_wrangling import *
import HMM.myBigQuery as myBQ
import HMM.scrub as scrub
import HMM.segment as segment

# <codecell>


