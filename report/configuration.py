import numpy as np
from collections import namedtuple
# Ranges edited by TLH on 11/2 in part of Calibration overhaul.
# See TLH Personal Note Documentation
# Ranges re-edited for tool/task-specificity 2/4/13

default_kinematics = {
              'left':[]
              ,'right':[]
              }             

##Tool Grasp Ranges##
interchangable = {
                'ThG_L': {'min': -5.5, 'max': 17. }
                ,'ThG_R': {'min': -17., 'max': 5.5 }
                ,'Fg_L': {'min': -0.6, 'max': 150. }
                ,'Fg_R': {'min': -0.6, 'max': 150. }
                  }
needle_driver = {
                'ThG_L': {'min': -50., 'max': 50. }
                ,'ThG_R': {'min': -50., 'max': 50. }
                ,'Fg_L': {'min': -0.6, 'max': 150. }
                ,'Fg_R': {'min': -0.6, 'max': 150. }
                  }
clip_applier = {
                'ThG_R': {'min': 0., 'max': 10. }#Irrelevant, no grasp angle sensor
                ,'Fg_R': {'min': -0.6, 'max': 250. }#can generate huge force values w/ staples
                  }
##Expected Ranges for Non-Grasp-Related Sensors##
not_gr_ranges = {		
			'%Time_V1'	: {'min': 0., 'max': None }
			, 'J1_L'  	: {'min': -10., 'max': 100. }
			, 'J2_L'  	: {'min': -85., 'max': 45. }
			, 'Lin_L' 	: {'min': -7., 'max': 10. }
			, 'Rot_L' 	: {'min': -720., 'max': 720. }
			, 'J1_R'	: {'min': -10., 'max': 100. }
			, 'J2_R'	: {'min': -85., 'max': 45. }
			, 'Lin_R'	: {'min': -7., 'max': 10. }
			, 'Rot_R'	: {'min': -720., 'max': 720. }
			, 'X_L'		: {'min': -26., 'max': 26. }
			, 'Y_L'		: {'min': -17., 'max': 12. }
			, 'Z_L'		: {'min': -8., 'max': 15. }
			, 'X_R'		: {'min': -26., 'max': 26. }
			, 'Y_R'		: {'min': -17., 'max': 12. }
			, 'Z_R'		: {'min': -8., 'max': 15. }
		}
##Task-Specific Ranges##
ranges = {
        0 : dict(interchangable.items() + not_gr_ranges.items() )
        ,1 : 
        ,2 : 
        ,3 : 
    }

isClipTask = lambda f: True if f[-5 :]=='3.txt' else False
stringNaN = lambda m: 'NaN' if np.isnan(m) else m

toolRight = "EdgeToolIdRightHex"
toolLeft = "EdgeToolIdLeftHex"

rating = lambda t: 'fail' if t else 'pass'

conf =  lambda x: testnan(x)

def testnan(x):
    try:
        float(x)
        return x
    except:
        return np.NaN


        
names = ['%Time_V1', 'J1_L', 'J2_L', 'Lin_L', 'Rot_L', 'ThG_L', 'Fg_L', 'J1_R', 'J2_R', 'Lin_R', 'Rot_R', 'ThG_R', 'Fg_R', 'X_L', 'Y_L', 'Z_L', 'X_R', 'Y_R', 'Z_R']
formats = [np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float, np.float]
dtype = {'names' : names, 'formats' : formats}
converterdict = {0: conf, 1: conf, 2: conf, 3: conf, 4: conf, 5: conf, 6: conf, 7: conf, 8: conf, 9: conf, 10: conf, 11: conf, 12: conf, 13: conf, 14: conf, 15: conf, 16: conf, 17: conf, 18: conf}

sensors = {'J1'  : ('J1_L', 'J1_R')
		 , 'J2'  : ('J2_L', 'J2_R') 
		 , 'Lin' : ('Lin_L', 'Lin_R')
		 , 'Rot' : ('Rot_L', 'Rot_R')
		 , 'ThG' : ('ThG_L', 'ThG_R')
		 , 'Fg'  : ('Fg_L', 'Fg_R')
		 , 'X'   : ('X_R', 'X_R')
		 , 'Y'   : ('Y_R', 'Y_R')
		 , 'Z'   : ('Z_R', 'Z_R')}
