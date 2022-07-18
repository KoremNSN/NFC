 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:36:15 2021

@author: Nachshon Korem PhD

This script will follow the test if prople feel fear of threat from electric shock

The biopack manual contorl should be set the following way:
    1. the STM100 checkbox should be checked.
    2. lower panel should show read + input
    3. all channels should be on '0'
    4. read continiously should be checked.

"""

from psychopy.hardware.labjacks import U3
from psychopy.iohub import launchHubServer # Import port accsess
from psychopy import visual, core, event, gui, monitors 
import numpy as np
import datetime, os, time, random

class subject:
    
    # declare all experiment variables
    
    def __init__(self, sub_n):
        """
        This function initate all parameters and create psychopy obnjects for the experiment

        Parameters
        ----------
        sub_n : Integer
            Create a Subject object.

        Returns
        -------
        None.

        """
        self.subjectID = sub_n # get subject number
        
        # create a time stamp at the bigining of the run
        date=datetime.datetime.now()
        self.time_stamp = str(date.day) + str(date.month) + str(date.year) + str(date.hour) + str(date.minute) + str(date.second)
        
        self.t_exp = time.time() # time the exp started
        # create file and folder for the run
        self.cwd = os.getcwd()
        fileName = self.cwd + '/data/nFC' + str(self.subjectID) + '_' + str(self.time_stamp)
        if not os.path.isdir('data/'):
           os.makedirs('data/')
        self.dataFile = open(fileName+'.csv', 'w')
                
        self.lj = U3() # open port for LabJack

        
        #writes headers for the output file
        self.dataFile.write('sub,Condition,Group,trial_n,phase,stim,prob,probRT,rating,ratingRT,onset,avoid,avoidrt,shock,shockrt\n')
        self.trial_n = 0
        self.avoided = 0
        self.self_inf = 0
        self.mon = monitors.Monitor('acer')
    
    def init_screen(self):
        # create a window object
        self.win = visual.Window(monitor=self.mon, color=[0,0,0], fullscr=True, size = [1920, 1080])
       
        # creates the visual objects for the experiment
        self.fixation = visual.Circle(self.win, radius = 10, fillColor = 'black', lineColor = 'black', units = 'pix')
        self.Text = visual.TextStim(self.win, text = "", pos = (0, 0), font = 'Courier New', height = 0.08,
                                    anchorHoriz = 'center', anchorVert = 'center', color = 'black', units = 'norm')
        self.rect = visual.Rect(self.win, units = "norm", width = 0.5, height = 0.5, fillColor = 'black', lineColor = 'Grey', pos = (0, 0)) # Pic?
        self.scaleShock = visual.RatingScale(self.win, scale = '', stretch = 2, showAccept = False, labels = ['Never', 'Everytime'],
                                        low = 1, high=  100, tickHeight = 0, singleClick = True) # VAS
        self.scaleLike = visual.RatingScale(self.win, scale = '', stretch = 2, showAccept = False, labels = ['Negative', 'Positive'],
                                        low = 1, high=  100, tickHeight = 0, singleClick = True)
        
        self.circle = visual.Circle(self.win, radius = 100, fillColor = 'red' ,color = 'red', units = 'pix')
        
        self.mouse = event.Mouse()
       
        if int(self.subjectID) % 2 == 0: # colors of stims
            self.stim = {"CSplus" : "blue", "CSminus" : "yellow"}
        else:
            self.stim = {"CSplus" : "yellow", "CSminus" : "blue"}
            
        self.group = random.randint(0, 3) # list were created using the helper_function.py file. counterbalnce between the orders
        self.Condition = int(self.subjectID) % 3 # Should I look for a better method to sellect group gui?
        


#%% shock calibration

    def shock_calibration(self):
        """
        This function is used to calibrate the shock level. 
        It is a simple loop that produce a shock.
        It zeros and than sends 1 on the 7 channel of the LJ.
        """
        win = visual.Window(monitor=self.mon, color=[0,0,0], fullscr=True, size = [1920, 1080])
        Text = visual.TextStim(win, text = "", pos = (0, 0), font = 'Courier New', height = 0.08,
                               anchorHoriz = 'center', anchorVert = 'center', color = 'black', units = 'norm')
        
        Text.text = 'shock intensity calibration'
        Text.draw()
        win.flip()
        event.waitKeys()
        
        
        while True:
            self.lj.setFIOState(7,0)
            Text.text = 'get ready'
            Text.draw()
            win.flip()
            time.sleep(1)
            self.lj.setFIOState(7,1)
            time.sleep(0.1)
            self.lj.setFIOState(7,0)
 
            Text.text = 'did you feel it? "5" to accept'
            Text.draw()
            win.flip()
            buttonPress=event.waitKeys()
                 
            if buttonPress == ['5']:
                break
        win.close()

#%% TOBii calibration

    def TOBii_calibration(self):
        """
        This procedure calibrates the TOBii
        """
        iohub_config = {'eyetracker.hw.tobii.EyeTracker':
                        {'name': 'tracker', 'runtime_settings': {'sampling_rate': 60}}} # TOBii configuration
            
        io = launchHubServer(**iohub_config) # lunch TOBii
        self.tracker = io.devices.tracker # create a TOBii instance
        self.tracker.runSetupProcedure() # run caliobration
        self.tracker.setRecordingState(True) # start recording
        
        gotSample=False
        while gotSample == False: # not sure why is it in a loop (taken from reversal script)
            sample=self.tracker.getLastSample()
            if sample!=None:
                self.getLength=len(sample) # creates an array (len = 50) the size of a complete sample of Tobii. 
                gotSample=True
        
        self.etData=np.zeros(self.getLength + 8) # add number of experiment spesific coulmns.

#%%      
    def TOBii_record(self, color, offset, stim=True, circle=False, mouse=False, fixation=False, text=False):
        
        etTemp=np.zeros(self.getLength + 8)
    
        onset = time.time()
        if mouse:
                buttons = self.mouse.getPressed()
        
        if stim:
            self.rect.draw()
        if circle:
            self.circle.draw()
        if fixation:
            self.fixation.draw()
        if text:
            self.Text.draw()
        self.win.flip()
        
        if mouse:
            while time.time() - onset < offset:
                eyeSample=np.array(self.tracker.getLastSample())
                fullSample = np.append([self.subjectID, self.phase, self.trial_n, color, stim, circle, fixation, text], eyeSample)
                etTemp = np.vstack([etTemp, fullSample])
                buttons = self.mouse.getPressed()
                
                if buttons[0] == 1:
                    self.etData=np.vstack([self.etData, self.etTemp])
                    return 1
        
        else:
            while time.time() - onset < offset:
                eyeSample=np.array(self.tracker.getLastSample())
                fullSample = np.append([self.subjectID, self.phase, self.trial_n, color, stim, circle, fixation, text], eyeSample)
                etTemp = np.vstack([etTemp, fullSample])
        
        self.etData=np.vstack([self.etData, etTemp])
        
        if mouse:
            return 0
 

#%% rating
    def rating(self, CS, real = True):
        """
        This function creates the VAS for the experiment. I use 2 VAS instead of 1 because the self.scale.labels = [] didn't work for some reason.
        It shows a predetermend text above the stim and the VAS below it

        Parameters
        ----------
        CS : string
            can be Either CSplus or CSminus as it takes the color from the original dictionary 
        real : Boolian, optional
             collect shock likelhood or just valence. The default is True.

        Returns
        -------
        If real == True return both shock liklihood and valence if real == False returns only valence.

        """
        
        # Check the color of the stim
        if CS[:3] == 'CSp':
            color = self.stim["CSplus"]
            self.rect.lineColor = 'Grey'
        else:
            color = self.stim["CSminus"]
            self.rect.lineColor = 'Grey'
            
        # prepare text location and stim color
        self.rect.fillColor = color
        self.Text.pos = (0, 0.5)
        
        # collect data about shock likelihood
        if real:
            self.Text.text = 'What is the likelihood of receiving a shock after this shape'
            self.scaleShock.reset()
            while self.scaleShock.noResponse:
                self.rect.draw()
                self.Text.draw()
                self.scaleShock.draw()
                self.win.flip()
                eyeSample=np.array(self.tracker.getLastSample())
                fullSample = np.append([self.subjectID, self.phase, self.trial_n, color, 'ranking', 'shock', 'False', 'False'], eyeSample)
                self.etData=np.vstack([self.etData, fullSample])
                
            shockprob, shockprobRT = self.scaleShock.getRating(), self.scaleShock.getRT()
        self.win.flip()
        time.sleep(0.2)
        # collect data about stim valence
        self.Text.text = 'What are your feelings toward this shape'
        self.scaleLike.reset()
        
        while self.scaleLike.noResponse:
            self.rect.draw()
            self.Text.draw()
            self.scaleLike.draw()
            self.win.flip()
            eyeSample=np.array(self.tracker.getLastSample())
            fullSample = np.append([self.subjectID, self.phase, self.trial_n, color, 'ranking', 'feel', 'False', 'False'], eyeSample)
            self.etData=np.vstack([self.etData, fullSample])
        
        self.win.flip()
        time.sleep(0.2)
        
        valence, valenceRT = self.scaleLike.getRating(), self.scaleLike.getRT()
        if real:
            return(shockprob, shockprobRT, valence, valenceRT)
        else:
            return(valence)
        
#%% trial

    def trial(self, CS, avoidance = False):
        """
        

        Parameters
        ----------
        CS : string
            can be Either CSplus or CSminus
        avoidance : boolian, optional
            IS this an avoidance trial. The default is False.

        Returns
        -------
        all outputs are saved to file.

        """
        self.trial_n += 1
        shock_time = 0.3 # how much time before the end of the stim the shock appears
        stim_time = 4 # how long to present the stim
        iti = 5 # time after stim until next fixation
        self.Text.pos = (0, 0) # zeros the text
        self.mouse.clickReset()
        event.clearEvents()
        self.lj.setFIOState(0,0)
        self.lj.setFIOState(7,0)
        
        # Checks is this is a reinforced trail
        US = False
        if (CS[-2:] == 'US'):
            US = True
            
            
        stimTime = stim_time - shock_time * US # adjust presentation of the stim for the shock (4-0.3)
        
        # check the color of the stim
        if CS[:3] == 'CSp':
            self.rect.fillColor = self.stim["CSplus"]
            self.rect.lineColor = 'Grey'
        else:
            self.rect.fillColor = self.stim["CSminus"]
            self.rect.lineColor = 'Grey'            
        
        # initate trial display
        self.TOBii_record(self.rect.fillColor, 1, stim=False, fixation=True)
        
        t0 = time.time() # get time of stim start
        
        self.lj.setFIOState(0,1)
        onset = t0 - self.t_exp # stim onset
        self.TOBii_record(self.rect.fillColor, 1)

        
        # the avoidance proc, should transfer to a function?
        if avoidance:
            self.circle.color = 'red'
            # the stim is displayed for 1 second before the button
            t0 = time.time()
            button = self.TOBii_record(self.rect.fillColor, 2, circle=True, mouse=True)
            RT =  time.time() - t0
            
            if button == 1: # if subject pressed
                self.circle.color = 'green'
                recTime = 3 - RT - shock_time * US
                self.TOBii_record(self.rect.fillColor, recTime, circle=True)
                self.avoided += 1 # avoidance counter
                US = False # cancel shock
                
            self.TOBii_record(self.rect.fillColor, 1 - shock_time * US, circle=True)
            self.dataFile.write('{0},{1},{2},{3},{4},{5},,,,,{6},{7},{8},,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, CS, onset, button, RT))
        else:
            self.TOBii_record(self.rect.fillColor, stimTime-1)
            self.dataFile.write('{0},{1},{2},{3},{4},{5},,,,,{6},,,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, CS, onset))
                
            
                 
        # initate shock procedure if US = True
        if US:
            self.lj.setFIOState(7,1)
            self.TOBii_record(self.rect.fillColor, shock_time)
            self.lj.setFIOState(7,0)
            
        self.lj.setFIOState(0,0)
                    
        # every 10 trials run rating function
        
        if (self.trial_n + 10) % 10 == 0:
            if random.randint(0, 1) == 1:
                CSPlikeRating, CSPlikeRT, CSPfeelRating, CSPfeellikeRT = self.rating('CSplus')
                CSMlikeRating, CSMlikeRT, CSMfeelRating, CSMfeellikeRT = self.rating('CSminus')
            else:
                CSMlikeRating, CSMlikeRT, CSMfeelRating, CSMfeellikeRT = self.rating('CSminus')
                CSPlikeRating, CSPlikeRT, CSPfeelRating, CSPfeellikeRT = self.rating('CSplus')
                
            self.dataFile.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},,,,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, 'CSplus', CSPlikeRating, CSPlikeRT, CSPfeelRating, CSPfeellikeRT))
            self.dataFile.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},,,,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, 'CSminus', CSMlikeRating, CSMlikeRT, CSMfeelRating, CSMfeellikeRT))
            self.win.flip()
            self.TOBii_record(self.rect.fillColor, 2, stim=False)

        else:
            self.win.flip()
            self.TOBii_record(self.rect.fillColor, iti, stim=False)
       

#%%

    def acquisition_inst(self):
        """
        run instractions for the experiemnet

        Returns
        -------
        None.

        """
        self.phase = "acq_inst"
        
        slide1 = ('Welcome to the Levy Decision Neuroscience Lab!\n' + 
                  'In the following experiment please try to stay as still as possible.\n' + 
                  'You are going to see different colored squares come up on the screen' + 
                  '\n\n\npress any key to continue')
        slide2 = 'Every couple of trials, you will be asked to rate your feelings toward the squares'
        slide3 = 'From now on, you may or may not be shocked.\nIf you receive a shock, try to see if there is a pattern associated with the shock.' + '\n\n\npress any key to continue'
        slide4 = 'Do you have any questions?'
        

        self.Text.text =slide1
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        self.lj.setFIOState(0,0)
        # create a baseline response to the squares (habituation)
        for trial in range(0, 3):
            t =[]
            if random.randint(0, 1) == 1:
                c1, c2, cl1, cl2 = "CSplus", "CSminus", self.stim["CSplus"], self.stim["CSminus"]

            else:
                c2, c1, cl2, cl1 = "CSplus", "CSminus", self.stim["CSplus"], self.stim["CSminus"]

            
            for color in (cl1, cl2):
                self.rect.color = color
                self.lj.setFIOState(0,1)
                t.append(time.time() - self.t_exp)
                
                self.TOBii_record(color, 1, stim=False)
                self.TOBii_record(color, 4)
                
                self.lj.setFIOState(0,0)
                self.TOBii_record(color, 5, stim=False)
            
                


            # write to file trial properties
            self.dataFile.write('{0},{1},{2},{3},{4},{5},,,,,{6},,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, c1, t[0]))
            self.dataFile.write('{0},{1},{2},{3},{4},{5},,,,,{6},,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, c2, t[1]))
                
        self.Text.text = slide2
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        #get baseline like/dislike for the squares
        if random.randint(0, 1) == 1:
            cspr = self.rating('CSplus', False)
            csmr = self.rating('CSminus', False)
        else:
            csmr = self.rating('CSminus', False)
            cspr = self.rating('CSplus', False)
            
        self.dataFile.write('{0},{1},{2},{3},{4},{5},,,{6},,,,,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, c1, cspr))
        self.dataFile.write('{0},{1},{2},{3},{4},{5},,,{6},,,,,,\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, c2, csmr))
            
        self.Text.pos = (0, 0)
        self.Text.text = slide3
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide4
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
           
    def acquisition(self):
        """
        runs the acuision phase of the experiment.
        phase 1 is 50% reinforcment
        phase 2 is 70% reinforcment
        based on self.group a list is chosen

        Returns
        -------
        None.

        """
        self.phase = "acq"
        
        a = [['CSplusUS', 'CSminus', 'CSplus',   'CSminus',  'CSminus',  'CSplusUS', 'CSminus', 'CSplusUS', 'CSplus', 'CSminus', 'CSplus', 'CSminus', 'CSplus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS'],
             ['CSplusUS', 'CSminus', 'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSminus', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus', 'CSminus', 'CSplus', 'CSminus', 'CSplus', 'CSplus'],
             ['CSplusUS', 'CSminus', 'CSminus',  'CSplus',   'CSminus',  'CSplus',   'CSminus', 'CSplusUS', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS', 'CSplus', 'CSminus', 'CSplus', 'CSplusUS'],
             ['CSplusUS', 'CSminus', 'CSminus',  'CSplusUS', 'CSminus',  'CSplus',   'CSminus', 'CSplus', 'CSplusUS', 'CSminus', 'CSplus', 'CSminus', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus']]
 
        b = [['CSplusUS', 'CSminus', 'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus', 'CSplus', 'CSminus', 'CSplusUS', 'CSplusUS', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus'],
             ['CSplusUS', 'CSminus', 'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus', 'CSplusUS', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus', 'CSplus', 'CSminus', 'CSplusUS', 'CSminus', 'CSminus'],
             ['CSplusUS', 'CSminus', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus', 'CSplusUS', 'CSplusUS', 'CSminus', 'CSminus', 'CSplusUS', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS', 'CSplus', 'CSminus', 'CSminus', 'CSplusUS'],
             ['CSminus',  'CSplus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSminus', 'CSplusUS', 'CSminus', 'CSplus', 'CSminus', 'CSplus', 'CSplusUS']]

        for i in range(len(a[self.group])):
            self.trial(a[self.group][i])
            
        for i in range(len(a[self.group])):
            self.trial(b[self.group][i])
    
        
    def extinction_inst(self):
        """
        If avoidance is run before extinction, explains that the button will no longer be avilable

        Returns
        -------
        None.

        """
        
        self.Text.pos = (0, 0)
        self.Text.text = 'In the next trials you will not have the possibility to press the button and avoid the shock\n\n\npress any key to continue'
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
    def extinction(self):
        """
        Runs the extinction phase. 40 trials no reinforcment

        Returns
        -------
        None.

        """
        self.phase = 'ext'
        
        
        exintction = [['CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSplus', 
                       'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus'], 
                      ['CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 
                       'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus'], 
                      ['CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus', 
                       'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSplus'], 
                      ['CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 
                       'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSminus', 'CSplus',  'CSplus',  'CSminus']]
        
        for i in range(len(exintction[self.group])):
            self.trial(exintction[self.group][i])
            
          
    def avoidance_inst(self):
        """
        Runs the avoidance instractions phase.
        This part includes 1 shock.

        Returns
        -------
        None.

        """
        
        self.Text.pos = (0, 0)
        
        #self.Text.pos = (0,0)
        slide1 = 'For the next part of the experiment we are giving you a bonus of $5.\nYou will be able to use the $5 in order to avoid shocks.' + '\n\n\npress any key to continue'
        slide2 = ('After the picture appear on the screen a red circle will appear.\nBy clicking the left mouse button you will prevent the shock.\nEach time you press it, $0.5 will be deducted from your bonus.' + 
                  '\n\n* You will not need to pay more than the $5 dollars in any case.' + '\n\n\n\n\n\npress any key to continue')
        slide3 = 'You will see the same set of shapes you have seen before.\nThis shape is just for instructions purposes.' + '\n\n\n\n\n\n\n\n\npress any key to continue'
        slide4 = 'A red dot will appear on top of it.\nIf you choose not to press it, you might receive a shock.' + '\n\n\n\n\n\n\n\n\npress any key to continue'
        slide5 = 'If you choose to press it, you will not receive a shock but $0.5 will be deducted from you bonus.' + '\n\n\n\n\n\n\n\n\npress any key to continue'
        
        self.Text.text = slide1
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide2
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide3
        self.rect.color = 'purple'
        self.rect.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide4
        self.circle.color = 'red'
        self.rect.draw()
        self.circle.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        self.lj.setFIOState(7,0)
        self.lj.setFIOState(7,1)
        time.sleep(0.3)
        self.lj.setFIOState(7,0)
        
        self.Text.text = slide5
        self.rect.draw()
        self.circle.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide5
        self.circle.color = 'green'
        self.rect.draw()
        self.circle.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
    
    def avoidance(self):
        """
        Runs the avoidance phase. In this phase subjects have 10 CS+US and 10 CS- and they pay $0.5 dollars to avoid the shock.

        Returns
        -------
        None.

        """
        self.phase = "avo"
        
        avoidance =  [['CSplusUS', 'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSminus', 'CSplusUS'],
                      ['CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus', 'CSminus'],
                      ['CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSminus', 'CSplusUS'],
                      ['CSplusUS', 'CSplusUS', 'CSminus',  'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSminus',  'CSplusUS', 'CSminus',  'CSplusUS', 'CSplusUS', 'CSminus',  'CSplusUS', 'CSminus', 'CSminus']]
        
        
        for i in range(len(avoidance[self.group])):
            self.trial(avoidance[self.group][i], True)
            
            
    def selfinflicting_inst(self):
        """
        Runs instractions for the self inflicting phase.
        Participants have the chance to earn $0.5 for everytime they press a button.
        In this part they recieve 1 shock.

        Returns
        -------
        None.

        """
        
        
        
        self.Text.pos = (0, 0)
          
        slide1 = 'In the next part of the experiment you will have a chance to win extra money.' + '\n\n\n\n\n\n\n\n\npress any key to continue'
        slide2 = 'Each time you see this dot on the screen\nyou can press on the left mouse button to receive additional payment of $0.5 and a shock.' + '\n\n\n\n\n\n\n\n\npress any key to continue'
        slide4 = 'If you do not press the left button,\nyou will not receive the shock and the money.' + '\n\n\n\n\n\n\n\n\npress any key to continue'
        
        self.Text.text = slide1
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide2
        self.circle.color = 'green'
        self.circle.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.lj.setFIOState(7,0)
        self.lj.setFIOState(7,1)
        time.sleep(0.3)
        self.lj.setFIOState(7,0)
        
        self.circle.color = 'red'
        self.circle.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
        self.Text.text = slide4
        self.circle.color = 'green'
        self.circle.draw()
        self.Text.draw()
        self.win.flip()
        event.waitKeys()
        
    def selfinflicting(self):
        """
        Chekcs how many timee do participants agree to recieve a shoick for $0.5.

        Returns
        -------
        None.

        """
        
        self.phase = "self"
        
        # 10 trials
        self.lj.setFIOState(0,0)
        for i in range(10):
            self.trial_n += 1
            t1 = 0
            
            self.mouse.clickReset()
            self.TOBii_record("fix_self", 0.5, stim=False, fixation=True) # fixation
            
            self.circle.color = 'green'
            t0 = time.time()
            # self.lj.setFIOState(0,1)

            button = self.TOBii_record("green_self", 4, stim=False, circle=True, mouse=True) # collect response if participants wants the shock
            
            if button == 1: # if shock
                t1 = time.time() - t0 #RT
                for j in range(3,0,-1): # count down to increase suspanse
                    self.Text.text = j
                    self.circle.color = 'red'
                    self.TOBii_record("fix_countdown", 1, stim=False, circle=True, text=True)
                    
                self.lj.setFIOState(7,0)
                self.lj.setFIOState(7,1)
                self.TOBii_record("US", 0.5, stim=False, circle=True)
                self.lj.setFIOState(7,0)
                self.self_inf += 1
                
            # self.lj.setFIOState(0,0)
            self.TOBii_record("fix_countdown", 6, stim=False) #ITI
            self.dataFile.write('{0},{1},{2},{3},{4},,,,,,,,,{5},{6}\n'.format(self.subjectID, self.Condition, self.group, self.trial_n, self.phase, button, t1))
            
            
    def goodbye(self):
        
        if self.Condition == 2:
            self.Text.text = 'Thank you for your participation\nYou collected extra $' + str(self.self_inf/2)
        else:
            self.Text.text = 'Thank you for your participation\nYou collected extra $' + str(5-self.avoided/2)
            
        self.Text.draw()
        self.win.flip()
        event.waitKeys(keyList = ['5'])
            
        
#%% end exp close everythiong

    def exp_end(self):
        fileName = self.cwd + '/data/el' + str(self.subjectID) + '_' + str(self.time_stamp) + '.csv'
         
        event.clearEvents()
        event.globalKeys.remove(key='q',modifiers = ['ctrl'])
        self.tracker.setRecordingState(False)
        self.dataFile.close()
        self.lj.close()
        self.dataFile.close()
        self.win.close()
        final_data = np.unique(self.etData, axis=0)
        np.savetxt(fileName, final_data, delimiter=",", fmt='%s')
        core.quit()

#%%

def main():        
    event.globalKeys.add(key='q',modifiers = ['ctrl'], func = core.quit) # add the option to abort experiment using ctrl+q
    expInfo = {'subject no':''}
    gui.DlgFromDict(expInfo, title='NFC', fixed=['dateStr']) # open GUI to collect subject number.
    sub = subject(expInfo['subject no']) # create a subject object with subject number
    
    
    sub.shock_calibration() 
    sub.TOBii_calibration() 
    sub.init_screen()
    sub.acquisition_inst()
    sub.acquisition()
    
    if sub.Condition == 0:
        sub.avoidance_inst()
        sub.avoidance()
        sub.extinction_inst()
        sub.extinction()
    elif sub.Condition == 1:
        sub.extinction()
        sub.avoidance_inst()
        sub.avoidance()
    else:
        sub.extinction()
        sub.selfinflicting_inst()
        sub.selfinflicting()
    
    sub.goodbye()
    sub.exp_end()
    
# %% 
if __name__ == '__main__':
    main()
