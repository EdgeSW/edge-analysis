import numpy as np
from collections import namedtuple
# Ranges edited by TLH on 11/2 in part of Calibration overhaul.
# See TLH Personal Note Documentation

kinematics = {
                 0: {'left':[]
                     , 'right':[]}
                ,1: {'left':[]
                     , 'right':[]}
                ,2: {'left':'-0.05140 0.57756 -0.81473 -6.60172 -0.81860 0.44294 0.36564 -14.56533 0.57205 0.68573 0.45003 13.97385 0.00000 0.00000 0.00000 1.00000'
                     , 'right':'-0.06266 0.57186 -0.81801 6.80131 0.82311 -0.43386 -0.36641 -14.57807 -0.56438 -0.69624 -0.44368 13.93098 0.00000 0.00000 0.00000 1.00000'}
                ,3: {'left':[]
                     , 'right':[]}
                ,4: {'left':[]
                     , 'right':[]}
                ,5: {'left':[]
                     , 'right':[]}
                ,6: {'left':'-0.06102 0.57388 -0.81667 -6.45954 -0.81560 0.44299 0.37223 -14.73327 0.57538 0.68879 0.44102 14.55966 0.00000 0.00000 0.00000 1.00000'
                     , 'right':'-0.05939 0.57102 -0.81883 6.68960 0.83328 -0.42326 -0.35565 -14.68017 -0.54962 -0.70341 -0.45085 14.02663 0.00000 0.00000 0.00000 1.00000'}
                ,7: {'left':[]
                     , 'right':[]}
                ,8: {'left':[]
                     , 'right':[]}
                ,9: {'left':[]
                     , 'right':[]}
                ,10: {'left':[]
                      , 'right':[]}
                ,11: {'left':[]
                      , 'right':[]}
                ,12: {'left':[]
                      , 'right':[]}                 


                }

ranges = {		
			'%Time_V1'	: {'min': 0., 'max': None }
			, 'J1_L'  	: {'min': -10., 'max': 100. }
			, 'J2_L'  	: {'min': -85., 'max': 45. }
			, 'Lin_L' 	: {'min': -7., 'max': 10. }
			, 'Rot_L' 	: {'min': -367., 'max': 367. }
			, 'ThG_L'	: {'min': -5., 'max': 25. }
			, 'Fg_L'	: {'min': -0.5, 'max': 125. }
			, 'J1_R'	: {'min': -10., 'max': 100. }
			, 'J2_R'	: {'min': -85., 'max': 45. }
			, 'Lin_R'	: {'min': -7., 'max': 10. }
			, 'Rot_R'	: {'min': -367., 'max': 367. }
			, 'ThG_R'	: {'min': -25., 'max': 5. }
			, 'Fg_R'	: {'min': -0.5, 'max': 125. }
			, 'X_L'		: {'min': -26., 'max': 26. }
			, 'Y_L'		: {'min': -17., 'max': 12. }
			, 'Z_L'		: {'min': -8., 'max': 15. }
			, 'X_R'		: {'min': -26., 'max': 26. }
			, 'Y_R'		: {'min': -17., 'max': 12. }
			, 'Z_R'		: {'min': -8., 'max': 15. }
		}

isClipTask = lambda f: True if f[-5 :]=='3.txt' else False
stringNaN = lambda m: 'NaN' if np.isnan(m) else m

rating = lambda t: 'fail' if t else 'pass'

conf =  lambda x: testnan(x)

toolRight = "EdgeToolIdRight"
toolLeft = "EdgeToolIdLeft"

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

pSuture = ['InstrumentLeftFieldOfView', 'DistanceFromTargetDot', 'BuckledPenrose',
           'LessThan3KnotThrows','CanSlideOpen', 'AirKnot', 'BunnyEar',
           'AvulseModelFromBoard', 'BrokeSutureOrBentNeedle', 'DroppedNeedle']

pPegTransfer = ['InstrumentLeftFieldOfView', 'NumberDropped',
				'NonMidAirTransferBetweenHands','DroppedOutsideTaskRegion']

pCutting = ['InstrumentLeftFieldOfView', 'CuttingOutsideLines',
			 'ToreOrPokedHole', 'ScissorTipsNotPointedToInterior',
			 'AvulseTissueFromClamps', 'LeftToolIsScissors']

pClipApply = ['InstrumentLeftFieldOfView', 'FailedToPutMinimum2ClipsBetweenLines',
			  'FailedToPut4Clips', 'IncompleteCoaption', 'CrossingClips',
		 	 'StraightCutOnMiddleDottedLine', 'GraspedTheRenalArtery']
MetadatFieldNames = {'ProctorSuture' : ["AirKnot","AvulseModelFromBoard","EdgesAreNotApproximatedCloselyTogether",
									    "DroppedNeedle","BrokeSutureOrBentNeedle", "BunnyEar","BrokeSuture",
									    "InstrumentLeftFieldOfView","BuckledPenrose","LessThan3KnotThrows",
									    "DistanceFromTargetDot", "BentNeedle",
									    "DistanceFromTargetDotRight","DistanceFromTargetDotLeft",
									    "CanSlideOpen"]

                     , 'ProctorPegTransfer' : ["NonMidAirTransferBetweenHands", "DroppedOutsideTaskRegion", "InstrumentLeftFieldOfView", "NumberDropped"]

                     , 'ProctorCutting' : ["LeftToolIsScissors", "NumberOfTimesOutsideTheLine", "ScissorTipsNotPointedToInterior",
										   "AvulseTissueFromClamps", "InstrumentLeftFieldOfView", "CuttingOutsideLines", 
										   "ToreOrPokedHole"] 

                     , 'ProctorClipApply' : ["CrossingClips", "FailedToPutMinimum2ClipsBetweenLines", 
											"InstrumentLeftFieldOfView", "StraightCutOnMiddleDottedLine", 
											"IncompleteCoaption", "GraspedTheRenalArtery", "FailedToPut4Clips"]}

metafields = ['MetaDataFileNameOnS3', 'DataFileNameOnS3', 'VideoFileNameOnS3', 
              'EdgeUnitId', 'IsPracticeTest', 'IsCalibrationTrace', 'EdgeToolIdLeft',
              'EdgeToolIdRight', 'ProctorCancelledTest', 'TestDurationInSeconds', 
              'EdgeSoftwareVersion', 'ProctorSuture', 'ProctorPegTransfer', 'ProctorCutting', 
              'ProctorClipApply']

