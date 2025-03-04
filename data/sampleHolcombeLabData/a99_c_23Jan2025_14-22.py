############################################################
### Hm, haven't tried waitBlank = True for a while
###For set-up on a new machine, some variables to consider
###
### useClock
### For setup of new experiment variant, variables to consider: 
### trialDurMin, trackVariableIntervMax
##############
from psychopy import sound, monitors, logging, visual, data, core
import psychopy.gui, psychopy.event, psychopy.info
import numpy as np, pandas as pd 
import itertools #to calculate all subsets
from copy import deepcopy
from math import atan, atan2, pi, cos, sin, sqrt, ceil, floor
import time, random, sys, platform, os, gc, io, warnings
import matplotlib.pyplot as plt
import helpersAOH
from helpersAOH import openMyStimWindow
try:
    import pylink #to turn off eyetracker graphics environment after eyetracker calibration. pylink comes from Eyelink Developers Kit download
except Exception as e:
    print("When trying to import Eyelink's pylink library, an exception occurred:",str(e))
    print('pylink is not included in PsychoPy download, you have to download and install the Eyelink Developers Kit from the SR Research Forum website.')
try: 
    from analysisPython import logisticRegression as logisticR
except Exception as e:
    print("An exception occurred:",str(e))
    print('Could not import logisticRegression.py (you need that file in the analysisPython directory, which needs an __init__.py file in its directory too)')
try:
    from staircasing import staircaseAndNoiseHelpers
except Exception as e:
    print("An exception occurred in staircase_tester_.py:",str(e))
    print('Could not import staircaseAndNoiseHelpers.py (you need that file to be in the staircasing subdirectory, which needs an __init__.py file in it too)')
try:
    from eyetrackingCode import EyelinkHolcombeLabHelpers #imports from eyetrackingCode subfolder.
    #EyeLinkTrack_Holcombe class originally created by Chris Fajou to combine lots of eyelink commands to create simpler functions
except Exception as e:
    print("An exception occurred:",str(e))
    print('Could not import EyelinkHolcombeLabHelpers.py (you need that file to be in the eyetrackingCode subdirectory, which needs an __init__.py file in it too)')
try:
    from theory import publishedEmpiricalThreshes #imports from theory subfolder.
except Exception as e:
    print("An exception occurred:",str(e))
    print('Could not import publishedEmpiricalThreshes.py (you need that file to be in the theory subdirectory, which needs an __init__.py file in it too)')

eyetracking = False; eyetrackFileGetFromEyelinkMachine = False #very timeconsuming to get the file from the eyetracking machine over the ethernet cable, 
#sometimes better to get the EDF file from the Eyelink machine by hand by rebooting into Windows and going to 
useSound=True
quitFinder = True 
if quitFinder and ('Darwin' in platform.system()): #turn Finder off. Only know the command for MacOS (Darwin)
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
process_priority = 'realtime' # 'normal' 'high' or 'realtime', but don't know if this works
disable_gc = True

subject='temp'#'test'
autoLogging = False
quickMeasurement = False #If true, use method of gradually speeding up and participant says when it is too fast to track
demo = False
autopilot= False; simulateObserver=True; showOnlyOneFrameOfStimuli = False
if autopilot:  subject='auto'
feedback=True
exportImages= False #quits after one trial / output image
screenshot= False; screenshotDone = False;allowGUI = False; waitBlank = False
trackAllIdenticalColors = True#with tracking, can either use same colors as other task (e.g. 6 blobs but only 3 colors so have to track one of 2) or set all blobs identical color

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
respTypes=['order']; respType=respTypes[0]
rng_seed = int(time.time())
np.random.seed(seed=rng_seed); random.seed(rng_seed)

drawingAsGrating = True;  debugDrawBothAsGratingAndAsBlobs = False
antialiasGrating = False; #True makes the mask not work perfectly at the center, so have to draw fixation over the center
gratingTexPix=1024 #If go to 128, cue doesn't overlap well with grating #numpy textures must be a power of 2. So, if numColorsRoundTheRing not divide without remainder into textPix, there will be some rounding so patches will not all be same size

numRings=3
radii=np.array([2.5,7,15]) #[2.5,9.5,15]   #Need to encode as array for those experiments where more than one ring presented 

respRadius=radii[0] #deg
refreshRate= 100.0   #160 #set to the framerate of the monitor
useClock = True #as opposed to using frame count, which assumes no frames are ever missed
fullscr=1; scrn=0
#Find out if screen may be Retina because of bug in psychopy for mouse coordinates (https://discourse.psychopy.org/t/mouse-coordinates-doubled-when-using-deg-units/11188/5)
has_retina_scrn = False
import subprocess
if 'Darwin' in platform.system(): #Because want to run Unix commands, which won't work on Windows - only do it if Mac
    resolutionOfScreens = subprocess.check_output("system_profiler SPDisplaysDataType | grep -i 'Resolution'",shell=True)
    print("resolution of screens reported by system_profiler = ",resolutionOfScreens)
    if subprocess.call("system_profiler SPDisplaysDataType | grep -i 'retina'", shell=True) == 0:
        has_retina_scrn = True #https://stackoverflow.com/questions/58349657/how-to-check-is-it-a-retina-display-in-python-or-terminal
dlgBoxTitle = 'MOT, and no Mac Retina screen detected'
if has_retina_scrn:
    dlgBoxTitle = 'MOT. At least one screen is apparently a Retina screen'
# create a dialog box from dictionary 
infoFirst = { 'Autopilot':autopilot, 'Screen to use':scrn, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
OK = psychopy.gui.DlgFromDict(dictionary=infoFirst, 
    title=dlgBoxTitle, 
    order=['Autopilot','Screen to use', 'Screen refresh rate', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating',
            'Screen to use': '0 means primary screen, 1 means second screen'},
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
autopilot = infoFirst['Autopilot']
checkRefreshEtc = True
scrn = infoFirst['Screen to use']
#print('scrn = ',scrn, ' from dialog box')
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']

#trialDurMin does not include trackVariableIntervMax or trackingExtraTime, during which the cue is on.
trialDurMin = 2 #1
trackingExtraTime= 1.2 #giving the person time to attend to the cue (secs). This gets added to trialDurMin
trackVariableIntervMax = 2.5 #Random interval that gets added to trackingExtraTime and trialDurMin
if demo: 
    trialDurMin = 5; refreshRate = 60.; 
tokenChosenEachRing= [-999]*numRings
cueRampUpDur=0; #duration of contrast ramp from stationary, during cue
cueRampDownDur=0 #duration of contrast ramp down to the end of the trial

def maxTrialDur():
    return( trialDurMin+trackingExtraTime+trackVariableIntervMax )
badTimingCushion = 0.3 #Creating more of reversals than should need. Because if miss frames and using clock time instead of frames, might go longer
def maxPossibleReversals():  #need answer to know how many blank fields to print to file
    return int( ceil(      (maxTrialDur() - trackingExtraTime)  / timeTillReversalMin          ) )
def getReversalTimes():
    reversalTimesEachRing = [  [] for i in range(numRings)  ]
    for r in range(numRings): # set random reversal times
        thisReversalDur = trackingExtraTime
        while thisReversalDur< trialDurTotal+badTimingCushion:  
            thisReversalDur +=  np.random.uniform(timeTillReversalMin,timeTillReversalMax) #10000; print('WARNING thisReversalDur off') 
            reversalTimesEachRing[r].append(thisReversalDur)
    return reversalTimesEachRing
    
cueDur = cueRampUpDur+cueRampDownDur+trackingExtraTime  #giving the person time to attend to the cue (secs)
rampUpFrames = refreshRate*cueRampUpDur;   rampDownFrames = refreshRate*cueRampDownDur;
cueFrames = int( refreshRate*cueDur )
ballStdDev = 1.8 * 3 
#mouseChoiceArea = ballStdDev * 0.2 #debugAH #*0.8  # origin =1.3  #Now use a function for this,
units='deg' #'cm'
timeTillReversalMin = 0.5 #0.5; 
timeTillReversalMax = 2.0# 1.3 #2.9
colors_all = np.array([[1,-1,-1]] * 20)  #colors of the blobs (typically all identical) in a ring. Need as many as max num objects in a ring
cueColor =  np.array([1,1,1])
#monitor parameters
widthPixRequested = 800 #1440  #monitor width in pixels
heightPixRequested = 600  #900 #monitor height in pixels
monitorwidth = 38; #30  38.5 #monitor width in centimeters
viewdist = 50.; #57 cm
bgColor = [-1,-1,-1] #black background
monitorname = 'testMonitor' # 'mitsubishi' #in psychopy Monitors Center
if exportImages:
    fullscr=0; scrn=0
    widthPixRequested = 600; heightPixRequested = 450
    monitorwidth = 25.0
if demo:    
    scrn=0; fullscr=0
    widthPixRequested = 800; heightPixRequested = 600
    monitorname='testMonitor'
    allowGUI = True
    monitorwidth = 23#18.0

mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPixRequested,heightPixRequested) )
myWin = openMyStimWindow(mon,widthPixRequested,heightPixRequested,bgColor,allowGUI,units,fullscr,scrn,waitBlank,autoLogging)
myWin.setRecordFrameIntervals(False)

trialsPerCondition = 3

refreshMsg2 = ''
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy window instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    print('Finished runInfo- which assesses the refresh and processes of this computer')
    refreshMsg1 = 'Median frames per second ='+ str( np.round(1000./runInfo["windowRefreshTimeMedian_ms"],1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (1000./runInfo["windowRefreshTimeMedian_ms"]-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than ' + str(round(refreshRateTolerancePct,0)) + '%'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True

myWin.close() #have to close window to show dialog box
dlgLabelsOrdered = list() #new dialog box
session='a'
myDlg = psychopy.gui.Dlg(title="object tracking experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name or ID:', subject, tip='')
    dlgLabelsOrdered.append('subject')
    myDlg.addField('session:',session, tip='a,b,c,')
    dlgLabelsOrdered.append('session')
myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
dlgLabelsOrdered.append('trialsPerCondition')
pctCompletedBreaks = np.array([])
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
msgWrongResolution = ''
if checkRefreshEtc and (not demo) and (myWinRes != [widthPixRequested,heightPixRequested]).any():
    msgWrongResolution = 'Instead of desired resolution of '+ str(widthPixRequested)+'x'+str(heightPixRequested)+ ' pixels, screen apparently '+ str(myWinRes[0])+ 'x'+ str(myWinRes[1])
    myDlg.addText(msgWrongResolution, color='GoldenRod')
    print(msgWrongResolution)
myDlg.addText('To abort, press ESC at a trial response screen', color='DimGrey') #color names stopped working along the way, for unknown reason
myDlg.show()
if myDlg.OK: #unpack information from dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
       sessionEntered =thisInfo[dlgLabelsOrdered.index('session')]
       session = str(sessionEntered) #cast as str in case person entered a number
   trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()

if os.path.isdir('.'+os.sep+'dataRaw'):
    dataDir='dataRaw'
else:
    print('"dataRaw" directory does not exist, so saving data in present working directory')
    dataDir='.'
expname = ''
datafileName = dataDir+'/'+subject+ '_' + str(session) + '_' + expname+timeAndDateStr
if not demo and not exportImages:
    dataFile = open(datafileName+'.tsv', 'w')  # sys.stdout
    import shutil
    #Create a copy of this actual code so we know what exact version of the code was used for each participant
    ok = shutil.copy2(sys.argv[0], datafileName+'.py') # complete target filename given
    #print("Result of attempt to copy = ", ok)    
    logF = logging.LogFile(datafileName+'.log', 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.WARNING) #DEBUG means set the console to receive nearly all messges, INFO is for everything else, INFO, EXP, DATA, WARNING and ERROR 
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)
longerThanRefreshTolerance = 0.27
longFrameLimit = round(1000./refreshRate*(1.0+longerThanRefreshTolerance),3) # round(1000/refreshRate*1.5,2)
msg = 'longFrameLimit=' + str(longFrameLimit) + ' Recording trials where one or more interframe interval exceeded this figure '
logging.info(msg)
print(msg)
if msgWrongResolution != '':
    logging.error(msgWrongResolution)

logging.info("computer platform="+sys.platform)
#save a copy of the code as it was when that subject was run
logging.info('File that generated this = sys.argv[0]= '+sys.argv[0])
logging.info("has_retina_scrn="+str(has_retina_scrn))
logging.info('trialsPerCondition =' + str(trialsPerCondition))
logging.info('random number seed =' + str(rng_seed))
#Not a test - the final window opening
myWin = openMyStimWindow(mon,widthPixRequested,heightPixRequested,bgColor,allowGUI,units,fullscr,scrn,waitBlank,autoLogging)
myWin.setRecordFrameIntervals(False)

#Just roll with whatever wrong resolution the screen is set to
if (not demo) and (myWinRes != [widthPixRequested,heightPixRequested]).any():
    msgWrongResolutionFinal = ('Instead of desired resolution of '+ str(widthPixRequested)+'x'+str(heightPixRequested) 
        +' pixels, screen is apparently '+ str(myWinRes[0])+ 'x'+ str(myWinRes[1]) + ' will base calculations off that.')
    logging.warn(msgWrongResolutionFinal)
widthPix = myWin.size[0]
heightPix = myWin.size[1]
logging.info( 'Screen resolution, which is also being used for calculations, is ' + str(widthPix) + ' by ' + str(heightPix) )

pixelperdegree = widthPix / (atan(monitorwidth/viewdist) /np.pi*180)

myMouse = psychopy.event.Mouse(visible = 'true',win=myWin)
runInfo = psychopy.info.RunTimeInfo(
        win=myWin,    ## a psychopy window instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
logging.info('second window opening runInfo mean ms='+str(runInfo["windowRefreshTimeAvg_ms"]))
logging.info(runInfo)
logging.info('gammaGrid='+str(mon.getGammaGrid()))
logging.info('linearizeMethod='+str(mon.getLinearizeMethod()))

#Create Gaussian blob
blob = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)

labelBlobs = False #Draw the number of each Gaussian blob over it, to visualize the drawing algorithm better
if labelBlobs:
    blobLabels = list()
    for i in range(20): #assume no more than 20 objects
        label = str(i)
        blobText = visual.TextStim(myWin,text=label,colorSpace='rgb',color = (-1,-.2,-1),autoLog=False)
        blobLabels.append(blobText)

optionChosenCircle = visual.Circle(myWin, edges=32, colorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options
#Optionally show zones around objects that will count as a click for that object
clickableRegion = visual.Circle(myWin, edges=32, colorSpace='rgb',fillColor=(-1,-.7,-1),autoLog=autoLogging) #to show clickable zones
#Optionally show location of most recent click
clickedRegion = visual.Circle(myWin, edges=32, colorSpace='rgb',lineColor=None,fillColor=(-.5,-.1,-1),autoLog=autoLogging) #to show clickable zones
clickedRegion.setColor((-.1,.8,-1)) #show in yellow

circlePostCue = visual.Circle(myWin, radius=2*radii[0], edges=96, colorSpace='rgb',lineColor=(.5,.5,-.6),lineWidth=8,fillColor=None,autoLog=autoLogging) #visual postcue
#referenceCircle allows optional visualisation of trajectory
referenceCircle = visual.Circle(myWin, radius=radii[0], edges=32, colorSpace='rgb',lineColor=(-1,-1,1),autoLog=autoLogging) #visual postcue

blindspotFill = 0 #a way for people to know if they move their eyes
if blindspotFill:
    blindspotStim = visual.PatchStim(myWin, tex='none',mask='circle',size=4.8,colorSpace='rgb',color = (-1,1,-1),autoLog=autoLogging) #to outline chosen options
    blindspotStim.setPos([13.1,-2.7]) #AOH, size=4.8; pos=[13.1,-2.7] #DL: [13.3,-0.8]
fixatnNoise = True
fixSizePix = 6 #20 make fixation big so flicker more conspicuous
if fixatnNoise:
    checkSizeOfFixatnTexture = fixSizePix/4
    nearestPowerOfTwo = round( sqrt(checkSizeOfFixatnTexture) )**2 #Because textures (created on next line) must be a power of 2
    fixatnNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    fixation= visual.PatchStim(myWin,pos=(0,0), tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=autoLogging)
    fixationBlank= visual.PatchStim(myWin,pos=(0,0), tex=-1*fixatnNoiseTexture, colorSpace='rgb',mask='circle',size=fixSizePix,units='pix',autoLog=autoLogging)
else:
    fixation = visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(.9,.9,.9),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
    fixationBlank= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(-1,-1,-1),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
fixationPoint = visual.PatchStim(myWin,colorSpace='rgb',color=(1,1,1),mask='circle',units='pix',size=2,autoLog=autoLogging) #put a point in the center

#respText = visual.TextStim(myWin,pos=(0, -.5),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
NextText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
NextRemindPctDoneText = visual.TextStim(myWin,pos=(-.1, -.4),colorSpace='rgb',color= (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(.1, -.5),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
speedText = visual.TextStim(myWin,pos=(-0.5, 0.5),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',text="0.00rps",autoLog=False)
if useSound: 
    ringQuerySoundFileNames = [ 'innerring.wav', 'middlering.wav', 'outerring.wav' ]
    soundDir = 'sounds'
    lowSound = sound.Sound('E',octave=4, stereo = False, sampleRate = 44100, secs=.8, volume=1.0, autoLog=autoLogging)
    respPromptSounds = [-99] * len(ringQuerySoundFileNames)
    for i in range(len(ringQuerySoundFileNames)):
        soundFileName = ringQuerySoundFileNames[i]
        soundFileNameAndPath = os.path.join(soundDir, ringQuerySoundFileNames[ i ])
        respPromptSounds[i] = sound.Sound(soundFileNameAndPath, secs=.2, autoLog=autoLogging)
    corrSoundPathAndFile= os.path.join(soundDir, 'Ding44100Mono.wav')
    corrSound = sound.Sound(corrSoundPathAndFile, volume=0.3, autoLog=autoLogging)

stimList = []
doStaircase = True
# temporalfrequency limit test
numTargets =        [2,                 3] #[2]
numObjsInRing =     [4,                 8] #[4]      #Limitation: gratings don't align with blobs with odd number of objects

# Get all combinations of those two main factors
#mainCondsInfo = {
#    'numTargets':    [2, 2, 3, 3],
#    'numObjects':    [4, 8, 4, 8],
#}
combinations = list(itertools.product(numTargets, numObjsInRing))
# Create the DataFrame with all combinations
mainCondsDf = pd.DataFrame(combinations, columns=['numTargets', 'numObjects'])
mainCondsInfo = mainCondsDf.to_dict('list') #change into a dictionary, in list format

publishedThreshes = publishedEmpiricalThreshes.getAvgMidpointThreshes()
publishedThreshes = publishedThreshes[['numTargets', 'HzAvgPreviousLit']] #only want average of previous literature

mainCondsDf = pd.DataFrame( mainCondsInfo )
mainCondsDf = pd.merge(mainCondsDf, publishedThreshes, on='numTargets', how='left')
mainCondsDf['midpointThreshPrevLit'] = mainCondsDf['HzAvgPreviousLit'] / mainCondsDf['numObjects']
mainCondsDf = mainCondsDf.drop('HzAvgPreviousLit', axis=1)  #Use this Dataframe to choose the starting speed for the staircase and the behavior of the autopilot observer
                        

#Old way of setting all speeds manually:
#speedsEachNumTargetsNumObjects =   [ [ [0.5,1.0,1.4,1.7], [0.5,1.0,1.4,1.7] ],     #For the first numTargets condition
#                                     [ [0.2,0.5,0.7,1.0], [0.5,1.0,1.4,1.7] ]  ]  #For the second numTargets condition

#don't go faster than 2 rps at 120 Hz because of temporal blur/aliasing

maxTrialsPerStaircase = 500 #Just an unreasonably large number so that the experiment won't stop before the number of trials set by the trialHandler is finished
staircases = []
#Need to create a different staircase for each condition because chanceRate will be different and want to estimate midpoint threshold to match previous work
if doStaircase: #create the staircases
    for stairI in range(len(mainCondsDf)): #one staircase for each main condition
        descendingPsychometricCurve = True
        #the average threshold speed across conditions found by previous literature for young people
        avgAcrossCondsFromPrevLit = mainCondsDf['midpointThreshPrevLit'].mean()
        #Assume that first session is 'a', second session is 'b', etc.
        sessionNum = ord(session) - ord('a') + 1
        if sessionNum <= 1:  #give all the staircases the same starting value 
            startVal = 0.6 * avgAcrossCondsFromPrevLit #Don't go higher because this was the average for the young people only
        elif sessionNum == 2:
            startVal = avgAcrossCondsFromPrevLit
        elif sessionNum >= 3:
            startVal = 0.75 * avgAcrossCondsFromPrevLit

        startValInternal = staircaseAndNoiseHelpers.toStaircase(startVal, descendingPsychometricCurve)
        print('staircase startVal=',startVal,' startValInternal=',startValInternal)

        this_row = mainCondsDf.iloc[stairI]
        condition = this_row.to_dict() # {'numTargets': 2, 'numObjects': 4}
        
        nUp = 1; nDown=3 #1-up 3-down homes in on the 79.4% threshold. Make it easier if get one wrong. Make it harder when get 3 right in a row
        if nUp==1 and nDown==3:
            staircaseConvergePct = 0.794
        else:
            print('WARNING: dont know what staircaseConvergePct is')    
        minSpeed = .03# -999 #0.05
        maxSpeed= 1.8 #1.8    #1.8
        minSpeedForStaircase = staircaseAndNoiseHelpers.toStaircase(minSpeed, descendingPsychometricCurve)
        maxSpeedForStaircase = staircaseAndNoiseHelpers.toStaircase(maxSpeed, descendingPsychometricCurve)
        #if descendingPsychometricCurve
        if minSpeedForStaircase > maxSpeedForStaircase:
            #Swap values of the two variables
            minSpeedForStaircase, maxSpeedForStaircase = maxSpeedForStaircase, minSpeedForStaircase
        #print('for internals, minSpeedForStaircase=',minSpeedForStaircase, 'maxSpeedForStaircase=',maxSpeedForStaircase)
        staircase = data.StairHandler(
            extraInfo = condition,
            startVal=startValInternal,
            stepType='lin',
            stepSizes= [.3,.3,.2,.1,.1,.05],
            minVal = minSpeedForStaircase, 
            maxVal= maxSpeedForStaircase,
            nUp=nUp, nDown=nDown,  
            nTrials = maxTrialsPerStaircase)
    
        numPreStaircaseTrials = 0
        #staircaseAndNoiseHelpers.printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
        print('Adding this staircase to list')
        staircases.append(staircase)

#phasesMsg = ('Doing '+str(numPreStaircaseTrials)+'trials with speeds= TO BE DETERMINED'+' then doing a max '+ \
#              str(maxTrialsPerStaircase)+'-trial staircase for each condition:')
queryEachRingEquallyOften = False
#To query each ring equally often, the combinatorics are complicated because have different numbers of target conditions.
if queryEachRingEquallyOften:
    leastCommonMultipleSubsets = int( helpersAOH.calcCondsPerNumTargets(numRings,numTargets) )
    leastCommonMultipleTargetNums = int( helpersAOH.LCM( numTargets ) )  #have to use this to choose ringToQuery.
    #for each subset, need to counterbalance which target is queried. Because each element occurs equally often, which one queried can be an independent factor. But need as many repetitions as largest number of target numbers.
    # 3 targets . 3 subsets maximum. Least common multiple is 3. 3 rings that could be post-cued. That means counterbalancing requires 3 x 3 x 3 = 27 trials. NO! doesn't work
    # But what do you do when 2 targets, which one do you pick in the 3 different situations? Can't counterbalance it evenly, because when draw 3rd situation, half of time should pick one and half the time the other. Therefore have to use least common multiple of all the possible set sizes. Unless you just want to throw away that possibility. But then have different number of trials in 2 targets than in 3 targets.
    #		-  Is that last sentence true? Because always seem to be running leastCommonMultipleSubsets/numSubsetsThis for each numTargets
    #	 Check counterbalancing of numObjectsInRing*speed*numTargets*ringToQuery.  Leaving out whichIsTargetEachRing which is a list of which of those numTargets is the target.
    print('leastCommonMultipleSubsets=',leastCommonMultipleSubsets, ' leastCommonMultipleTargetNums= ', leastCommonMultipleTargetNums)
                    
for numObjs in numObjsInRing: #set up experiment design
    for nt in numTargets: #for each num targets condition,
      numObjectsIdx = numObjsInRing.index(numObjs)
      numTargetsIdx = numTargets.index(nt)
      if doStaircase: #Speeds will be determined trial-by-trial by the staircases. However, to estimate lapse rate,
        #we need occasional trials with a slow speed.
        speeds = [[.02,.1],'staircase','staircase','staircase','staircase']  #speeds = [0.02, 0.1, -99, -99, -99]
      else: 
        speeds= speedsEachNumTargetsNumObjects[  numTargetsIdx ][ numObjectsIdx ]
      for speed in speeds:
        ringNums = np.arange(numRings)
        if queryEachRingEquallyOften:
            #In case of 3 rings and 2 targets, 3 choose 2 = 3 possible ring combinations
            #If 3 concentric rings involved, have to consider 3 choose 2 targets, 3 choose 1 targets, have to have as many conditions as the maximum
            subsetsThis = list(itertools.combinations(ringNums,nt)) #all subsets of length nt from the rings. E.g. if 3 rings and nt=2 targets
            numSubsetsThis = len( subsetsThis );   print('numSubsetsThis=',numSubsetsThis, ' subsetsThis = ',subsetsThis)
            repsNeeded = leastCommonMultipleSubsets / numSubsetsThis #that's the number of repetitions needed to make up for number of subsets of rings
            for r in range( int(repsNeeded) ): #Balance different nt conditions. For nt with largest number of subsets, need no repetitions
              for s in subsetsThis: #to equate ring usage, balance by going through all subsets. E.g. 3 rings with 2 targets is 1,2; 1,3; 2,3
                  whichIsTargetEachRing = np.ones(numRings)*-999 #initialize to -999, meaning not a target in that ring.
                  for ring in s:
                      whichIsTargetEachRing[ring] = np.random.randint(0,numObjs-1,size=1)
                  print('numTargets=',nt,' whichIsTargetEachRing=',whichIsTargetEachRing,' and that is one of ',numSubsetsThis,' possibilities and we are doing ',repsNeeded,'repetitions')
                  for whichToQuery in range( leastCommonMultipleTargetNums ):  #for each subset, have to query one. This is dealed out to  the current subset by using modulus. It's assumed that this will result in equal total number of queried rings
                      whichSubsetEntry = whichToQuery % nt  #e.g. if nt=2 and whichToQuery can be 0,1,or2 then modulus result is 0,1,0. This implies that whichToQuery won't be totally counterbalanced with which subset, which is bad because
                                      #might give more resources to one that's queried more often. Therefore for whichToQuery need to use least common multiple.
                      ringToQuery = s[whichSubsetEntry];  #print('ringToQuery=',ringToQuery,'subset=',s)
                      for basicShape in ['circle']: #'diamond'
                        for initialDirRing0 in [-1,1]:
                                stimList.append( {'basicShape':basicShape, 'numObjectsInRing':numObjs,'speed':speed,'initialDirRing0':initialDirRing0,
                                        'numTargets':nt,'whichIsTargetEachRing':whichIsTargetEachRing,'ringToQuery':ringToQuery} )
        else: # not queryEachRingEquallyOften, because that requires too many trials for a quick session. Instead
            #will randomly at time of trial choose which rings have targets and which one querying.
            whichIsTargetEachRing = np.ones(numRings)*-999 #initialize to -999, meaning not a target in that ring. '1' will indicate which is the target
            ringToQuery = 999 #this is the signal to choose the ring randomly
            for basicShape in ['circle']: #'diamond'
                for initialDirRing0 in [-1,1]:
                    stimList.append( {'basicShape':basicShape, 'numObjectsInRing':numObjs,'speed':speed,'initialDirRing0':initialDirRing0,
                                'numTargets':nt,'whichIsTargetEachRing':whichIsTargetEachRing,'ringToQuery':ringToQuery} )            

trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method
print('len(stimList), which is the list of conditions, is =',len(stimList))
#print('stimList = ',stimList)
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
logging.info(  str('starting exp with name: "'+'TemporalFrequencyLimit'+'" at '+timeAndDateStr)   )
msg = 'numtrials='+ str(trials.nTotal)+', trialDurMin= '+str(trialDurMin)+ ' trackVariableIntervMax= '+ str(trackVariableIntervMax) + 'refreshRate=' +str(refreshRate)     
logging.info( msg )
print(msg)
msg = 'cueRampUpDur=' + str(cueRampUpDur) + ' cueRampDownDur= ' + str(cueRampDownDur) + ' secs'
logging.info(msg);
logging.info('task='+'track'+'   respType='+respType)
logging.info('ring radii=' + str(radii))
logging.info('drawingAsGrating=' + str(drawingAsGrating) +  ' gratingTexPix='+ str(gratingTexPix) + ' antialiasGrating=' + str(antialiasGrating))
logging.flush()

stimColorIdxsOrder=[[0,0],[0,0],[0,0]]#this was used for drawing blobs during LinaresVaziriPashkam stimulus, now just vestigial for grating

def decimalPart(x):
    return ( abs(x-floor(x)) )

def constructRingAsGratingSimplified(radii,numObjects,patchAngle,colors,stimColorIdxsOrder,gratingTexPix,blobToCue):
    #Will create the ring of objects (ringRadial) grating and also a ring grating for the cue, for each ring
    #patchAngle is the angle an individual object subtends, of the circle
    ringRadial=list(); cueRing=list(); 
    #The textures specifying the color at each portion of the ring. The ringRadial will have multiple cycles but only one for the cueRing
    myTexEachRing=list();cueTexEachRing=list();

    #grating texture is rendered in reverse order than is blobs version, but that won't matter if blobs all the same color
    angleSegment = 360./(numObjects*2)
    if gratingTexPix % (numObjects*2) >0: #gratingTexPix contains 2 patches, one for object and one for space between.
        #numCycles will control how many total objects there are around circle
        logging.warn('Culd not exactly render a numObjects*2='+str(numObjects*2)+'-segment pattern radially, will be off by '+str( (gratingTexPix%(numObjects*2))*1.0 /gratingTexPix ) )
    if patchAngle > angleSegment:
        msg='Error: patchAngle (angle of circle spanned by object) requested ('+str(patchAngle)+') bigger than maximum possible (' + str(angleSegment) 
        print(msg); logging.error(msg)

    #initialize list of textures for objects grating, one for each ring. Initialize with bgColor
    for i in range(numRings):
        myTexThis = np.zeros([gratingTexPix,3]) + bgColor[0] #start with all of texture = bgColor
        myTexEachRing.append( myTexThis )

    #initialize cueTex list with bgColor like myTexThis
    cueTexEachRing = deepcopy(myTexEachRing)
    #for i in range(numRings): cueTexEachRing[i][:] = [-1,-1,0.5] #initialized with dark blue for visualization

    #Entire cycle of grating is just one object and one blank space
    halfCyclePixTexture = gratingTexPix/2 
    #Calculate pix of patch. gratingTexPix is entire cycle, so patchAngle is proportion of angleSegment*2
    patchPixTexture = patchAngle/(angleSegment*2)* gratingTexPix
    patchPixTexture = round(patchPixTexture) #best is odd number, even space on either size
    patchFlankPix = round(    (halfCyclePixTexture-patchPixTexture)/2.     )
    patchAngleActual = patchPixTexture / gratingTexPix * (360./numObjects)
    if abs(patchAngleActual - patchAngle) > .04:
        msg = 'Desired patchAngle = '+str(patchAngle)+' but closest can get with '+str(gratingTexPix)+' gratingTexPix is '+str(patchAngleActual); 
        logging.warn(msg)
    #print('halfCyclePixTexture=',halfCyclePixTexture,' patchPixTexture=',patchPixTexture, ' patchFlankPix=',patchFlankPix)
    #patchFlankPix at 199 is way too big, because patchPixTexture = 114

    #set half of texture to color of objects
    start = 0
    end = start + halfCyclePixTexture #patchPixTexture  
    start = round(start); end = round(end) #don't round until now after did addition, otherwise can fall short if multiplication involved
    ringColor=list();
    for i in range(numRings):
        ringColor.append(colors[ stimColorIdxsOrder[i][0] ]) #assuming only one object color for each ring (or all the same)

    for i in range(numRings):
        myTexEachRing[i][start:end, :] = ringColor[i];
        #Color flanks (bgColor)
        # so object to subtend less than half-cycle, as indicated by patchAngle) by overwriting first and last entries of segment 
        myTexEachRing[i][start:start+patchFlankPix, :] = bgColor[0]; #one flank
        myTexEachRing[i][end-1-patchFlankPix:end, :]   = bgColor[0]; #other flank

    #Do cueTex ####################################################################################
    #Assign cueTex with object color (or yellow if debug)
    segmentTexCuePix = gratingTexPix* 1.0/numObjects  #number of texture pix of one object (not counting spaces in between)
    for ringI in range(numRings):
        for objectI in range(numObjects):
            #Fill in the cueTex object locations initially with red, so that it can be constantly shown on top of the objects ring
            #It's only one cycle for the entire ring, unlike the objects ring, so that can highlight just a part of it as the white cue.

            #First color in the entire segment
            start = objectI * (segmentTexCuePix)
            end = start + segmentTexCuePix/2.0
            start = round(start); end = round(end) #don't round until now after did addition, otherwise can fall short
            debugCue = False
            objectColor = ringColor[0] #conventionally, red
            if debugCue:
                objectColor = [1,1,0] #make cuing ring obvious by having all its objects be yellow
            cueTexEachRing[ringI][start:end, :] = objectColor
            #print('cueTex ringI=', ringI, ' objectI=',objectI,' start=',start,'end=',end, '[start,:] = ', cueTexEachRing[ringI][start, :])

            #Erase flanks (color with bgColor)
            patchCueProportnOfCircle = patchAngle / 360
            patchCueProportnOfCircle = patchCueProportnOfCircle*.98 #I can't explain why, but it's too big otherwise so spills into bg area
            #Calculate number of texture elements taken up by the object
            patchPixCueTex = patchCueProportnOfCircle * gratingTexPix
            #Calculate number of texture elements taken up by the entire area available to an object and its flanks
            objectAreaPixCueTex = (gratingTexPix / numObjects) / 2.0
            #Calculate number of texture elements taken up by the flankers.  That's the area available - those taken up by the object,
            # divide by 2 because there's a flank on either side.
            patchFlankCuePix = (objectAreaPixCueTex - patchPixCueTex) / 2   
            patchFlankCuePix = round(patchFlankCuePix) 
            #print('patchAngle=',patchAngle,'patchPixCueTex=',patchPixCueTex, 'patchFlankCuePix=',patchFlankCuePix, 'segmentTexCuePix=',segmentTexCuePix) #debugAH
            firstFlankStart = start
            firstFlankEnd = start+patchFlankCuePix
            #print('firstFlankStart=',firstFlankStart, ' firstFlankEnd=',firstFlankEnd)
            cueTexEachRing[ringI][ firstFlankStart:firstFlankEnd, :] = bgColor[0]
            secondFlankStart = end-1-patchFlankCuePix
            secondFlankEnd = end
            cueTexEachRing[ringI][ secondFlankStart:secondFlankEnd, :] = bgColor[0]
        
        #Color the cueTex segment to be cued white
        #only a portion of that segment should be colored, the amount corresponding to angular patch
        if blobToCue[ringI] >=0: #-999 means dont cue anything
            blobToCue_alignWithBlobs = -1 * blobToCue[ringI] #orientation for gratings is opposite direction than Descartes 
            blobToCue_relativeToGaussianBlobsCorrect = (blobToCue_alignWithBlobs) % numObjects
            cueStart = blobToCue_relativeToGaussianBlobsCorrect * (gratingTexPix/numObjects)
            cueEnd = cueStart + (gratingTexPix/numObjects)/2.
            #print("blobToCue =",blobToCue_relativeToGaussianBlobsCorrect, " cueStart=",cueStart, " cueEnd=",cueEnd)
            #the critical line that colors the actual cue
            cueTexEachRing[ringI][round(cueStart):round(cueEnd), :] =  -1 * bgColor[0]  
            #fill flankers with bgColor
            firstFlankStart = cueStart
            firstFlankEnd = cueStart + patchFlankCuePix
            cueTexEachRing[ringI][round(firstFlankStart):round(firstFlankEnd), :] =  bgColor[0]  # [.8,-1,.5] #opposite of bgColor (usually black), thus usually white 
            secondFlankStart = cueEnd-1-patchFlankCuePix
            secondFlankEnd = cueEnd
            cueTexEachRing[ringI][round(secondFlankStart):round(secondFlankEnd), :] =  bgColor[0]  # [.8,-1,.5] #opposite of bgColor (usually black), thus usually white 

    angRes = 100 #100 is default. I have not seen any effect. This is currently not printed to log file.
    ringRadialMask=[[0,0,0,1,1],[0,0,0,0,0,0,1,1],[0,0,0,0,0,0,0,0,0,0,1,1]]  #Masks to turn each grating into an annulus (a ring)

    for i in range(numRings): #Create the actual ring graphics objects, both the objects ring and the cue rings

        #Need to shift texture by halfCyclePixTexture/2 to center it on how Gabor blobs are drawn. Because Gabor blobs are centered on angle=0, whereas
        # grating starts drawing at angle=0 rather than being centered on it, and extends from there
        shiftToAlignWithGaussianBlobs = -1 * round(halfCyclePixTexture/2.)
        myTexEachRing[i] = np.roll( myTexEachRing[i], shiftToAlignWithGaussianBlobs, axis=0 )

        #Make myTexEachRing into a two-dimensional texture. Presently it's only one dimension. Actually it's possible psychopy automatically cycles it
        arr_ex = np.expand_dims(myTexEachRing[i], axis=0)
        # Duplicate along the new first dimension to make that the same length so we have a square matrix of RGB triplets
        repeatsWanted = len(myTexEachRing[i])
        myTex2dThisRing = np.repeat(arr_ex, repeatsWanted, axis=0)
        #print(myTex2dThisRing.shape)

        #Draw annular stimulus (ring) using radialGrating function. Colors specified by myTexEachRing.
        thisRing = visual.RadialStim(myWin, tex=myTex2dThisRing, color=[1,1,1],size=radii[i],
                            mask=ringRadialMask[i], # this is a 1-D mask dictating the behaviour from the centre of the stimulus to the surround.
                            radialCycles=0, #the ringRadialMask is radial and indicates that should show only .3-.4 as one moves radially, creating an annulus
                            angularCycles= numObjects,
                            angularRes=angRes, interpolate=antialiasGrating, autoLog=autoLogging)
        ringRadial.append(thisRing)

        #Create cueRing
        #Need to shift texture by object/2 to center it on how Gabor blobs are drawn. Because Gabor blobs are centered on angle=0, whereas
        # grating starts drawing at angle=0 rather than being centered on it, and extends from there
        shiftToAlignWithGaussBlobs = -1 * round( (gratingTexPix/numObjects) / 4 )
        cueTexThisRing = np.roll( cueTexEachRing[i], shiftToAlignWithGaussBlobs, axis=0 )
        #print("Did np.roll successfully change cueTex, before vs after EQUALS = ", np.array_equal(cueTexThisRing,cueTexEachRing[i]))  # test if same shape, same elements values
        #Make cueTexEachRing into a two-dimensional texture. Presently it's only one dimension. Actually it's possible psychopy automatically cycles it
        arr_ex = np.expand_dims(cueTexThisRing, axis=0)
        # Duplicate along the new first dimension to make that the same length so we have a square matrix of RGB triplets
        repeatsWanted = len(cueTexThisRing)
        cueTex2dThisRing = np.repeat(arr_ex, repeatsWanted, axis=0)
        #print(cueTex2dThisRing.shape)

        #draw cue grating for tracking task. Entire grating will be empty except for one white sector
        cueRing.append(visual.RadialStim(myWin, tex=cueTex2dThisRing, color=[1,1,1], size=radii[i], #cueTexInner is white. Only one sector of it shown by mask
                        mask=ringRadialMask[i], radialCycles=0, 
                        angularCycles=1, #only one cycle because no pattern actually repeats- trying to highlight only one sector
                        angularRes=angRes, interpolate=antialiasGrating, autoLog=autoLogging) )#depth doesn't work, I think was abandoned by Psychopy
    
    currentlyCuedBlob = blobToCue #this will mean that don't have to redraw 
    return ringRadial,cueRing,currentlyCuedBlob
    ######### End constructRingAsGratingSimplified ###########################################################

RFcontourAmp= 0.0
RFcontourFreq = 2.0
RFcontourPhase = 0
def RFcontourCalcModulation(angle,freq,phase): 
    modulation = sin(angle*freq + phase) #radial frequency contour equation, e.g. http://www.journalofvision.org/content/14/11/12.full from Wilkinson et al. 1998
    return modulation
    
def diamondShape(constSpeedOrConstRps,angle):
    def triangleWave(period, phase):
           #triangle wave is in sine phase (starts at 0)
           y = -abs(phase % (2*period) - period) # http://stackoverflow.com/questions/1073606/is-there-a-one-line-function-that-generates-a-triangle-wave
           #y goes from -period to 0.  Need to rescale to -1 to 1 to match sine wave etc.
           y = y/period*2 + 1
           #Now goes from -1 to 1
           return y
           
    if constSpeedOrConstRps: #maintain constant rps. So, draw the blob at the prescribed theta. But change the radius to correspond to a square.
        #As a consequence, will travel faster the more the direction differs from the circle, like around the corners
        #Theta varies from 0 to 2pi. Taking its cosine, gives x coordinate on circle.
        #Instead of taking cosine, I should just make it a linear ramp of x back and forth. That is, turn it into a triangle wave
        #Want 0 to pi to be -1 to 1
        x = triangleWave(pi,angle)
        y = triangleWave(pi, (angle-pi/2)%(2*pi ))
        #This will always describe a diamond. To change the shape would have to use vector rotation formula
    else: #constant speed, so
        #take theta not as the angle wanted, but what proportion (after being divided by 2pi) along the trajectory you want to go
        angle = angle % (2*pi) #modulus
        proportnTraj = angle/(2*pi)
        if (proportnTraj < 0) or (proportnTraj>1):
            print("Unexpected angle below 0!"); logging.error("Unexpected angle below 0!")
        #how do I go from proportnTraj either to x,y or to theta?
        #Analytic method is that as increase theta deviates from 4 points that touches circle, theta change is smaller for equal change in proportnTraj
        #Brute force method is to divide into 4 segments, below.
        zeroToFour = proportnTraj*4
        if zeroToFour < 1: #headed NW up the first quadrant
            x = 1 - (zeroToFour-0)
            y = (zeroToFour-0)
        elif zeroToFour < 2: #SW
            x = - (zeroToFour - 1)
            y = 1- (zeroToFour - 1)
        elif zeroToFour < 3: #SE
            x = -1+(zeroToFour - 2)
            y = - (zeroToFour - 2)
        elif zeroToFour < 4: #NE
            x = (zeroToFour-3)
            y = -1+(zeroToFour-3)
        else: logging.error("Unexpected zeroToFour="+ str(zeroToFour))
        #Max x is 1, meaning that it will be the diamond that circumscribes the unit circle.
        #Otherwise need to adjust by calculating the average eccentricity of such a diamond and compensating, which I never did.
        return x,y

ampTemporalRadiusModulation = 0.0 # 1.0/3.0
ampModulatnEachRingTemporalPhase = np.random.rand(numRings) * 2*np.pi
def xyThisFrameThisAngle(basicShape, radiiThisTrial, numRing, angle, thisFrameN, speed):
    #period of oscillation should be in sec
    r = radiiThisTrial[numRing]
    timeSeconds = thisFrameN / refreshRate
    def waveForm(type,speed,timeSeconds,numRing):
        if speed==0 and ampTemporalRadiusModulation==0:
            return 0 #this way don't get division by zero error when speed=0
        else:
            periodOfRadiusModulation = 1.0/speed#so if speed=2 rps, radius modulation period = 0.5 s
            modulatnPhaseRadians = timeSeconds/periodOfRadiusModulation * 2*pi + ampModulatnEachRingTemporalPhase[numRing]
            if type=='sin':
                return sin(modulatnPhaseRadians)
            elif type == 'sqrWave':
                ans = np.sign( sin(modulatnPhaseRadians) ) #-1 or 1. That's great because that's also sin min and max
                if ans==0: ans = -1+ 2*round( np.random.rand(1)[0] ) #exception case is when 0, gives 0, so randomly change that to -1 or 1
                return ans
            else: print('Error! unexpected type in radiusThisFrameThisAngle')
        
    if basicShape == 'circle':
        rThis =  r + waveForm('sin',speed,timeSeconds,numRing) * r * ampTemporalRadiusModulation
        rThis += r * RFcontourAmp * RFcontourCalcModulation(angle,RFcontourFreq,RFcontourPhase)
        x = rThis*cos(angle)
        y = rThis*sin(angle)
    elif basicShape == 'diamond': #actual square-shaped trajectory. Could also add all the modulations to this, later
        x,y = diamondShape(constSpeedOrConstRps = False, angle=angle)
        x*=r
        y*=r
    else: 
        print('Unexpected basicShape: ',basicShape)
    
    return x,y

def angleChangeThisFrame(speed,initialDirectionEachRing, numRing, thisFrameN, lastFrameN):
    angleMoveRad = initialDirectionEachRing[numRing] * speed*2*pi*(thisFrameN-lastFrameN) / refreshRate
    return angleMoveRad


def alignAngleWithBlobs(angleOrigRad):
    centerInMiddleOfSegment = 0 #360./numObjects/2.0  #if don't add this factor, won't center segment on angle and so won't match up with blobs of response screen
    angleDeg = angleOrigRad/pi*180
    angleCentered = angleDeg + centerInMiddleOfSegment
    angleCentered = -1*angleCentered #multiply by -1 because with gratings, orientations is clockwise from east, contrary to Cartesian coordinates
    angleCentered = angleCentered + 90 #To align with individual blob drawing method, and hence response screen, as revealed by  debugDrawBothAsGratingAndAsBlobs = True
    return angleCentered

def oneFrameOfStim(thisTrial,speed,currFrame,clock,useClock,offsetXYeachRing,initialDirectionEachRing,currAngleRad,blobToCueEachRing,isReversed,reversalNumEachRing,cueFrames): 
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
  global cueRing,ringRadial, currentlyCuedBlob #makes explicit that will be working with the global vars, not creating a local variable
  global angleIniEachRing, correctAnswers
  angleIniEachRingRad = angleIniEachRing

  #Determine what frame we are on
  if useClock: #Don't count on not missing frames. Use actual time.
    t = clock.getTime()
    n = round(t*refreshRate)
  else:
    n = currFrame

  if n<rampUpFrames:
        contrast = cos( -pi+ pi* n/rampUpFrames  ) /2. +.5 #starting from -pi trough of cos, and scale into 0->1 range
  elif rampDownFrames>0 and n > rampDownStart:
        contrast = cos(pi* (n-rampDownStart)/rampDownFrames ) /2.+.5 #starting from peak of cos, and scale into 0->1 range
  else: contrast = 1

  for numRing in range(numRings):
    angleMoveRad = angleChangeThisFrame(speed,initialDirectionEachRing, numRing, n, n-1)
    currAngleRad[numRing] = currAngleRad[numRing]+angleMoveRad*(isReversed[numRing])
    angleObject0Rad = angleIniEachRingRad[numRing] + currAngleRad[numRing]
    #Handle reversal if time for reversal
    if reversalNumEachRing[numRing] <= len(reversalTimesEachRing[numRing]): #haven't exceeded reversals assigned
        reversalNum = int(reversalNumEachRing[numRing])
        if len( reversalTimesEachRing[numRing] ) <= reversalNum:
            msg = 'Not enough reversal times allocated, reached ' +str(reversalNum)+ ' reversals at '+ str( round(reversalTimesEachRing[numRing][reversalNum-1],1) )
            msg=msg+ 'and still going (only allocated the following:' + str( np.around(reversalTimesEachRing[numRing],1) )+ ' n= ' + str(round(n,1))
            msg=msg+ ' current time ='+str( round(n/refreshRate,2) )+' asking for time of next one, will assume no more reversals'
            logging.error(msg)
            print(msg)
            nextReversalTime = 9999 #didn't allocate enough, will just not reverse any more
        else: #allocated enough reversals
            nextReversalTime = reversalTimesEachRing[numRing][ reversalNum ]
        if n > refreshRate * nextReversalTime: #have now exceeded time for this next reversal
            isReversed[numRing] = -1*isReversed[numRing]
            reversalNumEachRing[numRing] +=1

    if drawingAsGrating or debugDrawBothAsGratingAndAsBlobs:
        angleObject0Deg = alignAngleWithBlobs(angleObject0Rad)
        ringRadial[numRing].setOri(angleObject0Deg)   
        ringRadial[numRing].setContrast( contrast )
        ringRadial[numRing].draw()
        if  (blobToCueEachRing[numRing] != -999) and n< cueFrames:  #-999 means there's no? target in that ring
            #if blobToCue!=currentlyCuedBlob: #if blobToCue now is different from what was cued the first time the rings were constructed, have to make new rings
                #even though this will result in skipping frames
                cueRing[numRing].setOri(angleObject0Deg)
                #gradually make the cue become transparent until it disappears completely (opacity=0), revealing the object
                opacity = 1 - n*1.0/cueFrames  #linear ramp from 1 to 0
                #The above makes it transparent too quickly, so pass through a nonlinearity
                # curve that decelerates towards 1,1, so will stay white for longer
                opacity = sqrt( cos( (opacity-1)*pi/2 ) ) # https://www.desmos.com/calculator/jsk2ppb1yu
                cueRing[numRing].setOpacity(opacity)  
                cueRing[numRing].draw()
        #draw tracking cue on top with separate object? Because might take longer than frame to draw the entire texture
        #so create a second grating which is all transparent except for one white sector. Then, rotate sector to be on top of target
    if (not drawingAsGrating) or debugDrawBothAsGratingAndAsBlobs: #drawing objects individually, not as grating. This just means can't keep up with refresh rate if more than 4 objects or so
        #Calculate position of each object for this frame and draw them                
        for nobject in range(numObjects):
            angleThisObjectRad = angleObject0Rad + (2*pi)/numObjects*nobject
            x,y = xyThisFrameThisAngle(thisTrial['basicShape'],radii,numRing,angleThisObjectRad,n,speed)
            x += offsetXYeachRing[numRing][0]
            y += offsetXYeachRing[numRing][1]
            if nobject==blobToCueEachRing[numRing] and n< cueFrames: #cue in white
                weightToTrueColor = n*1.0/cueFrames #compute weighted average to ramp from white to correct color
                blobColor = (1.0-weightToTrueColor)*cueColor +  weightToTrueColor*colors_all[nobject]
                blobColor *= contrast #also might want to change contrast, if everybody's contrast changing in contrast ramp
                #print('weightToTrueColor=',weightToTrueColor,' n=',n, '  blobColor=',blobColor)
            else: blobColor = colors_all[0]*contrast
            #referenceCircle.setPos(offsetXYeachRing[numRing]);  referenceCircle.draw()
            blob.setColor( blobColor, log=autoLogging )
            blob.setPos([x,y])
            blob.draw()
            if labelBlobs: #for debugging purposes such as to check alignment with grating version
                blobLabels[nobject].setPos([x,y])
                blobLabels[nobject].draw()

  #Drawing fixation after stimuli rather than before because gratings don't seem to mask properly, leaving them showing at center 
  if n%2:
    fixation.draw()#flicker fixation on and off at framerate to see when skip frame
  else:
    fixationBlank.draw()
  fixationPoint.draw()
  
  if quickMeasurement:  #be careful - drawing text in Psychopy is time-consuming, so don't do this in real testing / high frame rate
    speedText.setText( str(round(currentSpeed,1)) )
    speedText.draw()
  if blindspotFill:
      blindspotStim.draw()
  return angleIniEachRingRad,currAngleRad,isReversed,reversalNumEachRing   
# #######End of function that displays the stimuli #####################################
########################################################################################

showClickableRegions = False #Every time you click, show every disc's clickable region 
showClickedRegion = True #Problem with code is it shows the largest ring's region always, even if the smaller ring is clicked
showClickedRegionFinal = True #Show the last click, that's actually on the cued ring
mouseClickAreaFractionOfSpaceAvailable = 0.9 #0.9 means 90% of the space available to the object is clickable
def calcMouseChoiceRadiusForRing(ring):
    #For ring, need to calculate the smallest distance to another object, 
    # and set mouseChoiceRadius for that ring to smaller than that
    #Determine the max number of objects that ever occur in a ring, because that determines how big the mouse click radius can be
    # together with how far apart the rings are.
    maxNumObjects = max(numObjsInRing)

    #Calculate for all rings even though just want to know one
    mouseChoiceRadiusEachRing = np.zeros(numRings)
    minAngleBetweenObjectsOnRing = 2*pi / maxNumObjects #angle between objects on a ring

    #ring0
    ring0distToNextRing = radii[1] - radii[0] #distance between centers of rings 0 and 1
    #Find distance between objects using the formula for a chord of a circle, 2r*sin(theta/2)
    distBetweenObjectsInRing0 = 2*radii[0]*sin(minAngleBetweenObjectsOnRing/2)
    mouseChoiceRadius = min(ring0distToNextRing/2, distBetweenObjectsInRing0/2)
    mouseChoiceRadiusEachRing[0] = mouseChoiceRadius

    #ring1
    if numRings > 1:
        if numRings > 2:
            ring2distToRing1 = radii[2] - radii[1] #distance between centers of rings 2 and 1
            ring1closestRingDist = min(ring0distToNextRing,ring2distToRing1)
        else:
            ring1closestRingDist = ring0distToNextRing
        distBetweenObjectsInRing1 = 2*radii[1]*sin(minAngleBetweenObjectsOnRing/2) #formula for chord of a circle
        mouseChoiceRadius = min(ring1closestRingDist/2, distBetweenObjectsInRing1/2)
        mouseChoiceRadiusEachRing[1] = mouseChoiceRadius

    #ring2
    if numRings > 2: #Calculate closest distance from ring2 to the other two rings
        ring2distToRing1 = radii[2] - radii[1] #distance between centers of rings 2 and 1
        distBetweenObjectsInRing2 = 2*radii[2]*sin(minAngleBetweenObjectsOnRing/2) #formula for chord of a circle
        mouseChoiceRadius = min(ring2distToRing1,distBetweenObjectsInRing2/2)
        mouseChoiceRadiusEachRing[2] = mouseChoiceRadius
    
    #print('Closest distance to another object, for each ring: ',mouseChoiceRadiusEachRing)
    return mouseClickAreaFractionOfSpaceAvailable * mouseChoiceRadiusEachRing[ring]

def collectResponses(thisTrial,speed,n,responses,responsesAutopilot, respPromptSoundFileNum, offsetXYeachRing,respRadius,currAngle,expStop):
    optionSets=numRings
    #Draw/play response cues
    timesRespPromptSoundPlayed=0
    if timesRespPromptSoundPlayed<1: #2
        if numRings > 1:
            if useSound: respPromptSounds[respPromptSoundFileNum].play()
        timesRespPromptSoundPlayed +=1
    #respText.draw()

    respondedEachToken = np.zeros([numRings,numObjects])  
    optionIdexs=list();baseSeq=list();numOptionsEachSet=list();numRespsNeeded=list()
    numRespsNeeded = np.zeros(numRings) #potentially one response for each ring
    for ring in range(numRings):
        optionIdexs.append([])
        noArray=list()
        for k in range(numObjects):
            noArray.append(colors_all[0])
        baseSeq.append(np.array(noArray))
        for i in range(numObjects):
            optionIdexs[ring].append(baseSeq[ring][i % len(baseSeq[ring])] )
        if ring == thisTrial['ringToQuery']:
            numRespsNeeded[ ring ] = 1
        else: numRespsNeeded[ ring ] = 0
        numOptionsEachSet.append(len(optionIdexs[ring]))
    respcount = 0;     tClicked = 0;       lastClickState=0;       mouse1=0
    for ring in range(optionSets): 
            responses.append( list() )
            zeros = [0]*int(numRespsNeeded[ring])
            responsesAutopilot.append( zeros )  #autopilot response is 0
    passThisTrial = False; 
    numTimesRespSoundPlayed=0
    while respcount < sum(numRespsNeeded): #collecting response  
        for optionSet in range(optionSets):  #draw this group (ring) of options
          for ncheck in range( numOptionsEachSet[optionSet] ):  #draw each available to click on in this ring
                angle =  (angleIniEachRing[optionSet]+currAngle[optionSet]) + ncheck*1.0/numOptionsEachSet[optionSet] *2.*pi
                stretchOutwardRingsFactor = 1
                x,y = xyThisFrameThisAngle(thisTrial['basicShape'],radii,optionSet,angle,n,speed)
                x = x+ offsetXYeachRing[optionSet][0]
                y = y+ offsetXYeachRing[optionSet][1]            
                if not drawingAsGrating and not debugDrawBothAsGratingAndAsBlobs:
                    blob.setColor(  colors_all[0], log=autoLogging )
                    blob.setPos([x,y])
                    blob.draw()

                #draw circles around selected items. Colors are drawn in order they're in in optionsIdxs
                opts=optionIdexs;
                if respondedEachToken[optionSet][ncheck]:  #draw circle around this one to indicate this option has been chosen
                       optionChosenCircle.setColor(array([1,-1,1]), log=autoLogging)
                       optionChosenCircle.setPos([x,y])
                       optionChosenCircle.draw()                
          #end loop for individual blobs 
          if drawingAsGrating: #then blobs are actually rectangles, to mimic grating wedges
            ringRadial[optionSet].draw()
        #end loop through rings

        #Draw visual response cue, usually ring to indicate which ring is queried
        if visuallyPostCue:
            circlePostCue.setPos( offsetXYeachRing[ thisTrial['ringToQuery'] ] )
            circlePostCue.setRadius( radii[ thisTrial['ringToQuery'] ] )
            circlePostCue.lineWidth = 4 * (thisTrial['ringToQuery'] + 1) #line width scales with eccentricity, via ring number
            circlePostCue.draw()
            if drawingAsGrating:
                circlePostCue.opacity = 0.3

        mouse1, mouse2, mouse3 = myMouse.getPressed()
        if mouse1 and lastClickState==0:  #only count this event if is a new click. Problem is that mouse clicks continue to be pressed for along time
            mouseX,mouseY = myMouse.getPos() 
            #supposedly in units of myWin, which is degrees, BUT
            mouseFactor = 1
            if (has_retina_scrn and scrn==0): #Because of a bug in Psychopy triggered by retina displays
                mouseFactor = 0.5
            mouseX = mouseX * mouseFactor 
            mouseY = mouseY * mouseFactor 
            if showClickedRegion:
                #Determine choiceRadius for the ring the person needs to respond to
                mouseChoiceRadius = calcMouseChoiceRadiusForRing( thisTrial['ringToQuery'] )
                clickedRegion.setPos([mouseX,mouseY])
                clickedRegion.setRadius(mouseChoiceRadius)
                clickedRegion.draw()
            for optionSet in range(optionSets):
                mouseChoiceRadius = calcMouseChoiceRadiusForRing(optionSet) 
                #print('mouseChoiceRadius=',round(mouseChoiceRadius,1), 'for optionSet=',optionSet)
                for ncheck in range( numOptionsEachSet[optionSet] ): 
                    angle =  (angleIniEachRing[optionSet]+currAngle[optionSet]) + ncheck*1.0/numOptionsEachSet[optionSet] *2.*pi #radians
                    x,y = xyThisFrameThisAngle(thisTrial['basicShape'],radii,optionSet,angle,n,speed)
                    x = x+ offsetXYeachRing[optionSet][0]
                    y = y+ offsetXYeachRing[optionSet][1]
                    #check whether mouse click was close to any of the colors
                    if showClickableRegions: #every disc's region revealed every time you click
                        clickableRegion.setPos([x,y]) 
                        clickableRegion.setRadius(mouseChoiceRadius) 
                        clickableRegion.draw()
                    #print('mouseXY=',round(mouseX,2),',',round(mouseY,2),'xy=',round(x,2),',',round(y,2), ' distance=',distance, ' mouseChoiceRadius=',mouseChoiceRadius)
                    #Colors were drawn in order they're in in optionsIdxs
                    distance = sqrt(pow((x-mouseX),2)+pow((y-mouseY),2))
                    if distance < mouseChoiceRadius:
                        c = opts[optionSet][ncheck] #idx of color that this option num corresponds to
                        if respondedEachToken[optionSet][ncheck]:  #clicked one that already clicked on
                            if lastClickState ==0: #only count this event if is a distinct click from the one that selected the blob!
                                respondedEachToken[optionSet][ncheck] =0
                                responses[optionSet].remove(c) #this redundant list also of course encodes the order
                                respcount -= 1
                                #print('removed number ',ncheck, ' from clicked list')
                        else: #clicked on new one, need to add to response    
                            numRespsAlready = len(  np.where(respondedEachToken[optionSet])[0]  )
                            #print('numRespsAlready=',numRespsAlready,' numRespsNeeded= ',numRespsNeeded,'  responses=',responses)   
                            if numRespsAlready >= numRespsNeeded[optionSet]:
                                pass #not allowed to select this one until de-select other
                            else:
                                respondedEachToken[optionSet][ncheck] = 1 #register this one has been clicked
                                responses[optionSet].append(c) #this redundant list also of course encodes the order
                                respcount += 1  
                                print('added  ',ncheck,'th response to clicked list')
                            if showClickedRegionFinal: #Selected something from the correct ring, now show its region
                                clickableRegion.setPos([x,y]) 
                                clickableRegion.setRadius(mouseChoiceRadius) 
                                clickableRegion.draw()                                
                #print 'response=', response, '  respcount=',respcount, ' lastClickState=',lastClickState, '  after affected by click'
           #end if mouse clicked
           
        for key in psychopy.event.getKeys():       #check if pressed abort-type key
              if key in ['escape']: # ['escape','q']:
                  expStop = True
                  respcount = 1
              
        lastClickState = mouse1
        if autopilot: 
            respcount = 1
            for i in range(numRings):
                for j in range(numObjects):
                    respondedEachToken[i][j] = 1 #must set to True for tracking task with click responses, because it uses to determine which one was clicked on
        if blindspotFill:
            blindspotStim.draw()

        myWin.flip(clearBuffer=True)  
        if screenshot and ~screenshotDone:
           myWin.getMovieFrame()       
           screenshotDone = True
           myWin.saveMovieFrames('respScreen.jpg')
       #end response collection loop for non-'track' task
    #if [] in responses: responses.remove([]) #this is for case of tracking with click response, when only want one response but draw both rings. One of responses to optionset will then be blank. Need to get rid of it
    return responses,responsesAutopilot,respondedEachToken, expStop
    ####### #End of function definition that collects responses!!!! #################################################
    
print('Starting experiment of',trials.nTotal,'trials, starting with trial 0.')
#print header for data file
print('trialnum\tsubject\tsession\tbasicShape\tnumObjects\tspeed\tinitialDirRing0', end='\t', file=dataFile)
print('fixatnPeriodFrames', end='\t',file=dataFile) #So know when important part of eyetracking begins
print('orderCorrect\ttrialDurTotal\tnumTargets', end= '\t', file=dataFile) 
for i in range(numRings):
    print('whichIsTargetEachRing',i,  sep='', end='\t', file=dataFile)
print('ringToQuery',end='\t',file=dataFile)
for i in range(numRings):   dataFile.write('direction'+str(i)+'\t')
for i in range(numRings):   dataFile.write('respAdj'+str(i)+'\t')
for r in range(numRings):
    for j in range(maxPossibleReversals()):
        dataFile.write('rev'+str(r)+'_'+str(j)+'\t')  #reversal times for each ring
print('timingBlips\tnumLongFramesAfterFixation\tnumLongFramesAfterCue', file=dataFile)
#end of header

trialClock = core.Clock()
stimClock = core.Clock()
trialNum=0; numTrialsOrderCorrect=0; numAllCorrectlyIdentified=0; blueMistakes=0; expStop=False; framesSaved=0;
thisTrial = trials.next()
trialDurTotal=0;
ts = list();

if eyetracking:
    EDF_fname_local=('EyeTrack_'+subject+'_' + str(session) + '_' + timeAndDateStr+'.EDF')
    nameForRemoteEDF4charsMax = subject + str(session)
    if len(nameForRemoteEDF4charsMax) > 4:
        print('ERROR: stem of EDF eyetracker machine filename should not exceed 4 characters, because need four more for ".EDF", but yours is currently:',
                nameForRemoteEDF4charsMax, ' so I am sorry but I will now QUIT!')
        core.quit()

    my_tracker = EyelinkHolcombeLabHelpers.EyeLinkTrack_Holcombe(myWin,trialClock,
                                                                 nameForRemoteEDF4charsMax,1, 'HV5',(255,255,255),(0,0,0),False,(widthPix,heightPix))

randomStartAngleEachRing = True
randomInitialDirExceptRing0 = True
oppositeInitialDirFirstTwoRings = True

while trialNum < trials.nTotal and expStop==False:
    helpersAOH.accelerateComputer(1,process_priority, disable_gc) #I don't know if this does anything
    if quickMeasurement:
        maxSpeed = 1.0; numObjects = 10; numTargets = 3
        # create a dialog box from dictionary 
        infoFirst = { 'maxSpeed':maxSpeed, 'numObjects':numObjects, 'numTargets':numTargets  }
        manualParams = psychopy.gui.DlgFromDict(dictionary=infoFirst, title='Quick speed limit measurement', 
            order=['maxSpeed','numObjects', 'numTargets'], 
            tip={'Maximum speed for speed ramp': 'How many objects','How many targets': 'no more than 3'}
            )
        maxSpeed = infoFirst['maxSpeed']
        numObjects = infoFirst['numObjects']
        numTargets = infoFirst['numTargets']
    if not OK.OK:
        print('User cancelled from dialog box'); core.quit()
    
    if not queryEachRingEquallyOften: #then need to randomly set ringToQuery and whichIsTargetEachRing
        #To determine whichRingsHaveTargets, sample from 0,1,...,numRings by permuting that list
        rings = list(range(numRings) )
        random.shuffle(rings) 
        whichRingsHaveTargets = rings[ 0:thisTrial['numTargets'] ]
        #print("should be -999 at this point: thisTrial['whichIsTargetEachRing'] = ", thisTrial['whichIsTargetEachRing'])
        #Randomly assign a target object for each ring that is meant to have a target
        for r in whichRingsHaveTargets:
            thisTrial['whichIsTargetEachRing'][r] = np.random.randint(0,thisTrial['numObjectsInRing'])
        #Randomly pick ring to query. 
        random.shuffle(whichRingsHaveTargets) 
        thisTrial['ringToQuery'] = whichRingsHaveTargets[0]
        #print("thisTrial['numTargets']=",thisTrial['numTargets'], " thisTrial['whichIsTargetEachRing'] = ", thisTrial['whichIsTargetEachRing'], " thisTrial['ringToQuery']",thisTrial['ringToQuery'])
        
    colorRings=list();preDrawStimToGreasePipeline = list()
    isReversed= list([1]) * numRings #always takes values of -1 or 1
    reversalNumEachRing = list([0]) * numRings
    if randomStartAngleEachRing:
        angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
    else: 
        angleIniEachRing = [0]*numRings
    currAngle = list([0]) * numRings
    if randomInitialDirExceptRing0:
        initialDirectionEachRing = list( np.random.randint(0,1,size=[numRings]) *2 -1 ) #randomise initial direction of each ring
        initialDirectionEachRing[0] = thisTrial['initialDirRing0']
        if oppositeInitialDirFirstTwoRings and numRings>1:
            initialDirectionEachRing[1] = -1*initialDirectionEachRing[0]
    else:
        initialDirectionEachRing = [ thisTrial['initialDirRing0'] ] * numRings
    trackVariableIntervDur=np.random.uniform(0,trackVariableIntervMax) #random interval tacked onto tracking to make total duration variable so cant predict final position
    trialDurTotal = maxTrialDur() - trackVariableIntervDur
    trialDurFrames= int( trialDurTotal*refreshRate )
    rampDownStart = trialDurFrames-rampDownFrames
    #print('trialDurTotal=',np.around(trialDurTotal,2),' trialDurFrames=',np.around(trialDurFrames,2), 'refreshRate=',np.around(refreshRate) ) 
    xyTargets = np.zeros( [thisTrial['numTargets'], 2] ) #need this for eventual case where targets can change what ring they are in
    numDistracters = numRings*thisTrial['numObjectsInRing'] - thisTrial['numTargets']
    xyDistracters = np.zeros( [numDistracters, 2] )

    reversalTimesEachRing = getReversalTimes()
    numObjects = thisTrial['numObjectsInRing']
    centerInMiddleOfSegment =360./numObjects/2.0
    blobsToPreCue= thisTrial['whichIsTargetEachRing'] # [0,1,2] #debug 
    core.wait(.1)
    myMouse.setVisible(False)  #Doesn't seem to work any longer
    myMouse.setPos(newPos=(0,-15*3)) #Try to move mouse pointer offscreen. Supposedly it's in the window's units (deg) but that doesn't seem true, at least on Retina    
    if eyetracking: 
        my_tracker.startEyeTracking(trialNum,calibTrial=True,widthPix=widthPix,heightPix=heightPix) # tell eyetracker to start recording
            #and calibrate and drift-correct. It tries to draw on the screen to do the calibration.
        pylink.closeGraphics()  #Don't allow eyelink to still be able to draw because as of Jan2024, we can't get it working to have both Psychopy and Eyelink routines to draw to the same graphics environment
        my_tracker.sendMessage('trialDurTotal='+str(trialDurTotal))
    fixatnMinDur = 0.8
    fixatnVariableDur = 0.5
    fixatnPeriodFrames = int(   (fixatnMinDur + np.random.rand(1)*fixatnVariableDur)   *refreshRate)  #random interval between 800 and 1300ms
    for i in range(fixatnPeriodFrames):
        if i%2:
            fixation.draw()
        else: fixationBlank.draw()
        myWin.flip() #clearBuffer=True)  
    trialClock.reset()
    for L in range(len(ts)):
        ts.remove(ts[0]) #clear ts array, in case that helps avoid memory leak
    if eyetracking:
        my_tracker.sendMessage('Fixation pre-stimulus period of ' + str(fixatnPeriodFrames*refreshRate)+ 'now ending for trialnum=' + str(trialNum) ) 
    stimClock.reset()

    if drawingAsGrating or debugDrawBothAsGratingAndAsBlobs: #construct the gratings
        gratingObjAngle = 20; #the angle an individual object subtends, of the circle
        increaseRadiusFactorToEquateWithBlobs = 2.1 #Have no idea why, because units seem to be deg for both. Expect it to only be a bit smaller due to mask
        radiiGratings = radii*increaseRadiusFactorToEquateWithBlobs
        ringRadial,cueRing,currentlyCuedBlob = \
                constructRingAsGratingSimplified(radiiGratings,thisTrial['numObjectsInRing'],gratingObjAngle,colors_all,
                                                 stimColorIdxsOrder,gratingTexPix,blobsToPreCue)
        preDrawStimToGreasePipeline.extend([ringRadial[0],ringRadial[1],ringRadial[2]])
    core.wait(.1)

    if not doStaircase and not quickMeasurement:
        currentSpeed = thisTrial['speed'] #In normal experiment, no speed ramp
    elif quickMeasurement: #in quick measurement mode, which uses a speed ramp
        speedThisTrial = maxSpeed
        currentSpeed = 0.01
        speedRampStep = 0.01
        print('ramp currentSpeed =',round(currentSpeed,2))
    elif doStaircase: #speed will be set by staircase corresponding to this condition, or occasional ultra-slow speed as specified by speeds,
          #to estimate lapseRate
        if thisTrial['speed'] == 'staircase':
            #Work out which staircase this is, by finding out which row of mainCondsDf this condition is
            rownum = mainCondsDf[ (mainCondsDf['numTargets'] == thisTrial['numTargets']) &
                                  (mainCondsDf['numObjects'] == thisTrial['numObjectsInRing'] )       ].index
            condnum = rownum[0] #Have to take[0] because it was a pandas Index object, I guess to allow for possibility of multiple indices
            staircaseThis = staircases[condnum]
            speedThisInternal = staircaseThis.next()
            speedThisTrial = staircaseAndNoiseHelpers.outOfStaircase(speedThisInternal, staircaseThis, descendingPsychometricCurve) 
            #print('speedThisInternal from staircase=',round(speedThisInternal,2),'speedThisTrial=',round(speedThisTrial,2))
        else: #manual occasional speed, probably ultra-slow to estimate lapseRate
            #print('Non-staircase slow speed!, speedThisTrial=',thisTrial['speed'], ' will pick a random one')
            if len(thisTrial['speed']) >1: #randomly pick from speeds specified, not deterministic to avoid having too many trials 
                # while also trying to have overwhelming majority be staircase
                speedThisTrial = random.choice(thisTrial['speed'])
            else:
                speedThisTrial = thisTrial['speed']
        currentSpeed = speedThisTrial #no speed ramp
           
    t0=trialClock.getTime(); #t=trialClock.getTime()-t0         
    #the loop for this trial's stimulus!
    for n in range(trialDurFrames): 
        offsetXYeachRing=[ [0,0],[0,0],[0,0] ]
        if currentSpeed < speedThisTrial:
            currentSpeed = currentSpeed + speedRampStep
        if basicShape == 'diamond':  #scale up speed so that it achieves that speed in rps even though it has farther to travel
            perimeter = radii[numRing]*4.0
            circum = 2*pi*radii[numRing]
            finalspeed = speedThisTrial * perimeter/circum #Have to go this much faster to get all the way around in same amount of time as for circle
        #print('currentSpeed=',currentSpeed) 

        (angleIni,currAngle,isReversed,reversalNumEachRing) = \
            oneFrameOfStim(thisTrial,currentSpeed,n,stimClock,useClock,offsetXYeachRing,initialDirectionEachRing,currAngle,blobsToPreCue,isReversed,reversalNumEachRing,cueFrames) #da big function

        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1
        myWin.flip(clearBuffer=True)
        
        #time management. Record how long this frame was. Later, check if it was longer than the refresh rate.
        t=trialClock.getTime()-t0;
        ts.append(t);
        if useClock: #Rather than necessarily showing every frame, allowing for skipped frames by showing frame that is correct for this time.
            #But that means that n may not reach trialDurFrames until after have reached end of trial, so need to quit rather than 
            #let the stimuli keep going around and around
            if t > trialDurTotal:
                msg="Current time is already past trial duration, must not have kept up with some frames, breaking out of loop"; print(msg)
                break
        if showOnlyOneFrameOfStimuli: #abort after just one frame
            break
    #End of trial stimulus loop!
    
    if eyetracking:
        my_tracker.stopEyeTracking() 
    #clear mouse buffer in preparation for response, which may involve clicks
    psychopy.event.clearEvents(eventType='mouse')

    #end of big stimulus loop
    helpersAOH.accelerateComputer(0,process_priority, disable_gc) #turn off stuff that sped everything up. But I don't know if this works.
    #check for timing problems
    interframeIntervs = np.diff(ts)*1000 #difference in time between successive frames, in ms
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded longerThanRefreshTolerance of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0:
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                msg= 'trialnum=' + str(trialNum) + ' ' + longFramesStr
                print(msg, file=logF)
                print(msg)
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:  flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    #print >>logF, 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) ) 
    #Informally, I noticed that it's only at the beginning of a trial that I see frequent fixation flicker (timing blips), so
    #separately report num timingBlips after fixation and after target cueing, because it dont' really matter earlier
    numLongFramesAfterFixation = len(  np.where( idxsInterframeLong > fixatnPeriodFrames )[0] )
    print('numLongFramesAfterFixation=',numLongFramesAfterFixation)
    numLongFramesAfterCue = len(    np.where( idxsInterframeLong > fixatnPeriodFrames + cueFrames )[0]   )
    print('numLongFramesAfterCue=',numLongFramesAfterCue) 
    #end timing check
    myMouse.setVisible(True)
    
    passThisTrial=False
    
    #Create response prompt / postcue
    visuallyPostCue = True
    ringQuerySoundFileNames = [ 'innerring.wav', 'middlering.wav', 'outerring.wav' ]
    soundDir = 'sounds'
    if numRings==3:
        respPromptSoundFileNum = thisTrial['ringToQuery']
    else: #eg if numRings==2:
        respPromptSoundFileNum = thisTrial['ringToQuery']*2 #outer, not middle for ring==1
    
    if useSound:
        respPromptSoundPathAndFile= os.path.join(soundDir, ringQuerySoundFileNames[ respPromptSoundFileNum ])
        respPromptSound = sound.Sound(respPromptSoundPathAndFile, secs=.2)

    postCueNumBlobsAway=-999 #doesn't apply to click tracking and non-tracking task

    responses = list();  responsesAutopilot = list()
    responses,responsesAutopilot,respondedEachToken,expStop = \
            collectResponses(thisTrial,currentSpeed,n,responses,responsesAutopilot,respPromptSoundFileNum,offsetXYeachRing,respRadius,currAngle,expStop)  #collect responses!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#####
    #print("responses=",responses,";respondedEachToken=",respondedEachToken,"expStop=",expStop)
    core.wait(.1)
    if exportImages:  #maybe catch one frame of response
        myWin.saveMovieFrames('exported/frame.png')    
        expStop=True        
    #Handle response, calculate whether correct, ########################################
    if autopilot:responses = responsesAutopilot
    if True: #not expStop: #if short on responses, too hard to write code to handle it so don't even try
        orderCorrect=0; numColorsCorrectlyIdentified=0; blueMistake=0;respAdj=list();sCorrect=list();targetCorrect=0;
        for l in range(numRings):
            if responses[l] !=[]: 
               tokenChosenEachRing[l]=np.where(respondedEachToken[l])  [0][0] 
               respAdjs= initialDirectionEachRing[l]*isReversed[l]*(tokenChosenEachRing[l]-thisTrial['whichIsTargetEachRing'][l])
               if respAdjs> numObjects/2. : respAdjs-= numObjects  #code in terms of closest way around. So if 9 objects and 8 ahead, code as -1
               if respAdjs < -numObjects/2. : respAdjs += numObjects
               respAdj.append(respAdjs)
               if tokenChosenEachRing[l]==thisTrial['whichIsTargetEachRing'][l]: 
                  sCorrects=1
                  sCorrect.append(sCorrects);
                  targetCorrect+=sCorrects
            else:
               respAdj.append(-999)
               sCorrect.append(0)
        if targetCorrect==1: orderCorrect = 3
        else: orderCorrect = 0

    if passThisTrial:   orderCorrect = -1    #indicate for data analysis that observer opted out of this trial, because think they moved their eyes

    #header print('trialnum\tsubject\tsession\tbasicShape\tnumObjects\tspeed\tinitialDirRing0\tangleIni
    print(trialNum,subject,session,thisTrial['basicShape'],thisTrial['numObjectsInRing'],
            speedThisTrial, #could be different than thisTrial['speed'] because staircase
            thisTrial['initialDirRing0'],sep='\t', end='\t', file=dataFile) #override newline end
    print(fixatnPeriodFrames, end='\t', file=dataFile) #So know when important part of eyetracking begins
    print(orderCorrect,'\t',trialDurTotal,'\t',thisTrial['numTargets'],'\t', end=' ', file=dataFile) 
    for i in range(numRings):  print( thisTrial['whichIsTargetEachRing'][i], end='\t', file=dataFile  )
    print( thisTrial['ringToQuery'],end='\t',file=dataFile )
    for i in range(numRings):dataFile.write(str(round(initialDirectionEachRing[i],4))+'\t') 
    for i in range(numRings):dataFile.write(str(round(respAdj[i],4))+'\t') 
    for k in range(numRings):
        for i in range(len(reversalTimesEachRing[k])):
            print(round(reversalTimesEachRing[k][i],4),'\t', end='', file=dataFile)
        for j in range(i+1,maxPossibleReversals()):
            print('-999\t', end='', file=dataFile)
    print(numCasesInterframeLong, file=dataFile, end='\t')
    print(numLongFramesAfterFixation, file=dataFile, end='\t')
    print(numLongFramesAfterCue, file=dataFile, end='\n')

    if autopilot and doStaircase and simulateObserver:
        chanceRate = 1.0 / thisTrial['numObjectsInRing']
        rownum = mainCondsDf[ (mainCondsDf['numTargets'] == thisTrial['numTargets']) &
                                  (mainCondsDf['numObjects'] == thisTrial['numObjectsInRing'] )       ].index
        condnum = rownum[0] #Have to take[0] because it was a pandas Index object, I guess to allow for possibility of multiple indices
        staircaseThis = staircases[condnum] #needed to look this up because on some trials, staircase is possibly not used (slow speed to estimate lapserate)
        threshold = staircaseThis.extraInfo['midpointThreshPrevLit']
        lapseRate = .05
        #print('simulating response with speedThisTrial=',round(speedThisTrial,2),'chanceRate=',chanceRate,'lapseRate=',lapseRate,'threshold=',threshold)
        correct_sim = staircaseAndNoiseHelpers.simulate_response(speedThisTrial,chanceRate,lapseRate,threshold,descendingPsychometricCurve)
        orderCorrect = correct_sim*3 #3 is fully correct
        #print('speedThisTrial=',speedThisTrial,'threshold=',round(threshold,2),'correct_sim=',correct_sim,'orderCorrect=',orderCorrect)
        
    numTrialsOrderCorrect += (orderCorrect >0)  #so count -1 as 0
    numAllCorrectlyIdentified += (numColorsCorrectlyIdentified==3)
    dataFile.flush(); logging.flush(); 

    if orderCorrect==3:
        correctForFeedback=1
    else:
        correctForFeedback=0
    if feedback and not expStop:
        if correctForFeedback and useSound:
            corrSound.play()
        else: #incorrect
            if useSound:
                lowSound.play()
    trials.addData('speedThisTrial',speedThisTrial)  #when doStaircase is true, this will often be different than thisTrial['speed]
    trials.addData('orderCorrect',orderCorrect)
    trials.addData('correctForFeedback',correctForFeedback)
    if doStaircase and (thisTrial['speed']=='staircase'):
        staircaseThis.addResponse(correctForFeedback) #add correct/incorrect to the staircase so it can calculate the next speed

    if trials.nTotal <= 10:
        breakTrialNums = [] #Only have breaks if more than 10 trials
    else: 
        breakTrialNums = np.round( pctCompletedBreaks/100. * trials.nTotal )
        breakTrialNums = breakTrialNums[breakTrialNums >= 3] #No point having a break before trial 3.
        #print('breakTrialNums=',breakTrialNums)
    trialNum+=1
    waitForKeyPressBetweenTrials = False
    if trialNum< trials.nTotal:
        pctDone =  (1.0*trialNum) / (1.0*trials.nTotal)*100
        NextRemindPctDoneText.setText( str(round(pctDone)) + '% complete' )
        NextRemindCountText.setText( str(trialNum) + ' of ' + str(trials.nTotal) )
        if np.isin(trialNum, breakTrialNums): 
            breakTrial = True
        else: breakTrial = False
        if breakTrial:
            for i in range(5):
                myWin.flip(clearBuffer=True)
                NextRemindPctDoneText.draw()
                NextRemindCountText.draw()
        waitingForKeypress = False
        if waitForKeyPressBetweenTrials or breakTrial:
            waitingForKeypress=True
            NextText.setText('Press "SPACE" to continue')
            NextText.draw()
            NextRemindCountText.draw()
            #NextRemindText.draw()
            myWin.flip(clearBuffer=True) 
        else:
            core.wait(0.15)
        while waitingForKeypress:
           if autopilot:
                waitingForKeypress=False
           elif expStop == True:
                waitingForKeypress=False
           for key in psychopy.event.getKeys():       #check if pressed abort-type key
                 if key in ['space']: 
                    waitingForKeypress=False
                 if key in ['escape','q']:
                    expStop = True
                    waitingForKeypress=False
        myWin.clearBuffer()
        thisTrial = trials.next()
        
    core.wait(.1); time.sleep(.1)
    #end trials loop  ###########################################################
if expStop == True:
    logging.info('User aborted experiment by keypress with trialNum=' + str(trialNum))
    print('User aborted experiment by keypress with trialNum=', trialNum)

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
msg = 'Finishing now, at ' + timeAndDateStr
logging.info(msg); print(msg)
#print('%correct order = ', round( numTrialsOrderCorrect*1.0/trialNum*100., 2)  , '% of ',trialNum,' trials', end=' ')
logging.flush(); dataFile.close();

if eyetracking:
  logging.info('eyetracking = ' + str(eyetracking))
  if eyetrackFileGetFromEyelinkMachine:
    eyetrackerFileWaitingText = visual.TextStim(myWin,pos=(-.1,0),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
    msg = 'Waiting for eyetracking file from Eyelink computer. Do not abort eyetracking machine or file will not be saved on this machine.'
    logging.info(msg); logging.flush();
    eyetrackerFileWaitingText.setText(msg)
    eyetrackerFileWaitingText.draw()
    myWin.flip()

    msg = my_tracker.closeConnectionToEyeTracker(EDF_fname_local) #this requests the data back and thus can be very time-consuming, like 20 min or more
    msg = "Message from closeConnectionToEyeTracker, which tries to get EDF file and close connection:" + msg
    print(msg); logging.info(msg) #""Eyelink connection closed successfully" or "Eyelink not available, not closed properly" also prints any error assocaited with getting the EDF file
  else:
    msg = 'You will have to get the Eyelink EDF file off the eyetracking machine by hand'
    print(msg); logging.info(msg)
else:
  logging.info('Didnt try to eyetrack because "eyetracking" was set to ' + str(eyetracking))
logging.flush();
myWin.close()

if doStaircase: #report staircase results
    meanReversalsEachStaircase = np.zeros( len(staircases) )
    # Create a new column and initialize with NaN or some default value
    mainCondsDf['meanReversal'] = np.nan

    for staircase in staircases: #Calculate staircase results
        print('condition of this staircase = ', staircase.extraInfo)
        #actualThreshold = mainCondsDf[ ] #query for this condition. filtered_value = df.query('numTargets == 2 and numObjects == 4')['midpointThreshPrevLit'].item()
        actualThreshold = staircase.extraInfo['midpointThreshPrevLit']
        print('Staircase should converge on the', str(100*staircaseConvergePct), '% threshold, whose actual value for this condition is', actualThreshold)
        #Average all the reversals after the first few.
        numReversals = len(staircase.reversalIntensities)
        numRevsToUse = max( 1, numReversals-2 ) #To avoid asking for less than 1 reversal
        finalReversals = staircaseAndNoiseHelpers.outOfStaircase(staircase.reversalIntensities[-numRevsToUse:],staircase,descendingPsychometricCurve)   
        meanOfFinalReversals = np.average( finalReversals )
        print('Mean of final', numRevsToUse,'reversals = %.2f' % meanOfFinalReversals)
        stairI = staircases.index(staircase)
        meanReversalsEachStaircase[ stairI ] = meanOfFinalReversals
        # Set the stairI row's 'meanReversal' value
        mainCondsDf.at[stairI, 'meanReversal'] = meanOfFinalReversals  # Indexing is 0-based in Python, so the 4th row is at index 3
    
    print('About to plot staircases')
    plt.rcParams["figure.figsize"] = (16, 7) #Note this will determine the size of all subsequently created plots.
    plt.subplot(121) #1 row, 1 column, which panel
    title = 'circle = mean of final reversals'
    if autopilot and simulateObserver:
        title += '\ntriangle = true threshold'
    plt.title(title)
    plt.xlabel("staircase trial")
    plt.ylabel("speed (rps)")

    colors = 'grby'
    for staircase in staircases:
        stairI = staircases.index(staircase)
        colorThis = colors[stairI]
        #print('About to get intensities this staircase')
        intensities = staircaseAndNoiseHelpers.outOfStaircase(staircase.intensities,staircase,descendingPsychometricCurve)
        if len(intensities)>0:
            plt.plot(intensities, colorThis+'-')
        #Calculate correct answer, to help visualize if staircase is converging on the right place
        actualThresh = staircase.extraInfo['midpointThreshPrevLit']
        if len(staircase.reversalIntensities)>0: #plot mean of last reversals
            #print('About to plot mean this staircase')
            lastTrial = len(staircase.intensities)
            plt.plot( lastTrial, meanReversalsEachStaircase[ stairI ], colorThis+'o' )
            #plot correct answer
            plt.plot( lastTrial+1, actualThresh, colors[stairI]+'<' )
    # save a vector-graphics format for future
    figDir = 'analysisPython'
    outputFile = os.path.join(figDir, 'lastStaircases.pdf') #Don't know why it saves as empty
    plt.savefig(outputFile)

#Plot percent correct by condition and speed for all trials, and then try to fit logistic regression.
trialHandlerDatafilename = datafileName + 'trialHandler.tsv'
df = trials.saveAsWideText(trialHandlerDatafilename,delim='\t')  #Only calling this to get the dataframe df
#If session was incomplete, then trials that didn't get to have value "--" in columns set dynamically, like speedThisTrial
# Create a boolean mask for where 'speedThisTrial' is '--'
dashes_mask = (df['speedThisTrial'] == '--')
all_false = (~dashes_mask).all()
if all_false:
    numLegitTrials = len(df)
    print('Session appears to have completed all (',len(df),'trials), because no double-dashes ("--") appear in the file')
    print('\ndtype=',df['speedThisTrial'].dtypes) #'object' means it probably includes strings, which probably happened because didn't complete all trials
    #But if I run autopilot with 10 trials even though it finishes ,I sometimes get object type, whereas with 1 autopilot trial I don't.
    #And when I open the file afterward with analyseTrialHandlerOutput.py, it works fine and has type float64
    #Need to convert from string to number
else:
    # Find the first True in the mask, which is the first trial that didn't complete
    first_row_with_dashes_num = dashes_mask.idxmax()
    numLegitTrials = first_row_with_dashes_num
    print('Num trials in dataframe (num rows)=',len(df), '. Num trials that experiment got through=', numLegitTrials)
    #Throw away all the non-legitimate trials
    df = df[:numLegitTrials]
    #print('Completed portion of session=',df)
    if numLegitTrials < 2:
        print('Forget it, I cannot analyze a one-trial experiment')
        quit()
# Convert to numeric. Shouldn't need this if session completes but because of psychopy bug (see above), do.
df['speedThisTrial'] = pd.to_numeric(df['speedThisTrial'])
df['numTargets'] = pd.to_numeric(df['numTargets'])
df['numObjectsInRing'] = pd.to_numeric(df['numObjectsInRing'])
df['correctForFeedback'] = pd.to_numeric(df['correctForFeedback'])
#Finished clean-up of dataframe that results from incomplete session

# set up plot
if doStaircase:
    plt.subplot(122) #Because already plotted staircases above
else:
    plt.subplot(111)
plt.ylabel("Proportion correct")
plt.xlabel('speed (rps)')
threshVal = 0.794
speedEachTrial = df['speedThisTrial']

print('trialNum=',trialNum)
#maxX = speedEachTrial.nlargest(1).iloc[0]
#print('maxX with nlargest=',maxX)
maxX = speedEachTrial.max()
plt.plot([0, maxX], [threshVal, threshVal], 'k--')  # horizontal dashed line
paramsEachCond = list()

#Fit logistic regressions
for condi, cond in mainCondsDf.iterrows():
    #actualThreshold = mainCondsDf[ ] #query for this condition. filtered_value = df.query('numTargets == 2 and numObjects == 4')['midpointThreshPrevLit'].item()
    # Create a mask to reference this specific condition in my df
    maskForThisCond = (df['numTargets'] == cond['numTargets']) & (df['numObjectsInRing'] == cond['numObjects'])
    condLabelForPlot= str( round(cond['numTargets']) ) + 'targets,' + str( round(cond['numObjects']) ) + 'objs'
    all_false = (~maskForThisCond).all()
    if all_false:
        print('No trials available for condition ',cond, 'so stopping plotting.')
        break

    dataThisCond =  df[ maskForThisCond  ]

    #Aggregate data into percent correct for plotting actual data
    grouped_df = dataThisCond.groupby(['speedThisTrial']).agg(
        pctCorrect=('correctForFeedback', 'mean'),
        n=('correctForFeedback', 'count')
    )
    aggregatedDf = grouped_df.reset_index()

    # plot points
    pointSizes = np.array(aggregatedDf['n']) * 5  # 5 pixels per trial at each point
    points = plt.scatter(aggregatedDf['speedThisTrial'], aggregatedDf['pctCorrect'], s=pointSizes,
        c= colors[condi], label = condLabelForPlot,
        zorder=10,  # make sure the points plot on top of the line
        )    

    #Get variables for logistic regression fit
    x = dataThisCond[['speedThisTrial' ]] #data[['numObjectsInRing','numTargets','speedThisTrial' ]]
    y = dataThisCond['correctForFeedback']
    y = y.values #because otherwise y is a Series for some reason
    #print('y=',y, 'type(y)=',type(y))

    parametersGuess = [1,-2]
    chanceRate = 1/ cond['numObjects']
    #fit data with logistic regression
    fitSucceeded = False
    if len(x) > 4: #don't even try unless have a bunch of trials for this condition
        with warnings.catch_warnings(): #https://stackoverflow.com/a/36489085/302378
            warnings.filterwarnings('error')
            try:
                parameters = logisticR.fit(x, y, chanceRate, parametersGuess)
                fitSucceeded = True
            except Warning as e:
                print('error when doing logistic fit:', e)
                fitSucceeded = False
                
    #predict psychometric curve from logistic regression
    if fitSucceeded:
        paramsEachCond.append(parameters)
        mypredicted = logisticR.predict(x,chanceRate,parameters)
        #print('logistic regression-predicted values=', mypredicted)
        # Create a new column 'predicted' and assign the values from mypredicted
        # to the rows matching the condition
        df.loc[maskForThisCond, 'logisticPredicted'] = mypredicted

        xForCurve = np.arange(0,1.6,.02)
        xForCurve = pd.DataFrame(xForCurve).to_numpy() #otherwise plot gives error on Windows
        predicted = logisticR.predict(xForCurve,chanceRate,parameters)
        predicted = (pd.DataFrame(predicted)).to_numpy() #otherwise plot gives error on Windows
        plt.plot( xForCurve, predicted, colors[condi]+'-' )

plt.legend()
#print('paramsEachCond=',paramsEachCond)
title = 'Data and logistic regression fit'
#if autopilot and simulateObserver:
#    title += 'triangle = true threshold'
plt.title(title)
outputFile = datafileName + '.pdf' #os.path.join(fileName, 'last.pdf')
plt.savefig(outputFile)
plt.show()

if quitFinder and ('Darwin' in platform.system()): #If turned Finder (MacOS) off, now turn Finder back on.
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)
print('Got to the end of the program and now quitting normally.')
core.quit()