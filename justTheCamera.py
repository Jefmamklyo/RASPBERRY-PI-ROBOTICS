#import cv library and assign to variable cv
import cv2 as cv
import threading
import numpy as np

import serial


###PID ENCAPSULATION ClASS #####
#______________________________#
import time







###################################
#Camera Encapsulation class #######
###################################
class CamManage:
    #Contructor 
    def __init__(self, camInt=0, width = 320, height =320):    
        self.cam = cv.VideoCapture(camInt, cv.CAP_V4L2)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        #---------Threading shared variables __________#

        self.frame = None #Stores captured frame and starts empty becuase no captured frame
        self.isRunning = False  #Thread loop running controls
        self.RCP = threading.Lock() #RCP is race condition prevention

        #__________________Homography Matricies_______________#

        self.srcPoints = np.float32([  #source points muilti dimenstional array

            [110,140], #top left
            [210,140], #top right
            [300,320], #bottom right
            [20, 320]   #bottom left
            ])

        self.dstPoints = np.float32([ #destination points muilti dimenstional array

            [0,0], #top left
            [320,0], #top right
            [320,320], #bottom left
            [0,320]    #bottom right   
        ])

        self.HM = cv.getPerspectiveTransform(self.srcPoints, self.dstPoints)
      
    def start(self):
        self.isRunning = True
        #Creates a 1 new daemon thread which will run the function update located within self or the class
        self.thread = threading.Thread(target = self.update, daemon=True)
        self.thread.start() #Starts the thread
    
    #defines what happens in the new thread
    def update(self):
        #reads cam and stores it in shared variable frane
        while self.isRunning:
            ret, frame = self.cam.read()
            #if ret is true/ stream exists
            if ret:
                with self.RCP:
                    self.frame= frame
        
    #returnlatest frame stored in self.frame
    def read(self):
        with self.RCP:
            return self.frame

    #TopDownView function
    def TopDownView(self,frame):
        warped = frame
        return warped

    def frame2(self, frame):
        frameTwo = self.TopDownView(frame)
        return frameTwo
    
    #frame processing
    def preProcessing(self, frame):

        #birds eye view
        frame = self.TopDownView(frame)
        frame2 = frame.copy()

        
        #hsv
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        
        #lower range RED

        lowerRed1 = np.array([0,120,70])
        upperRed1 = np.array([10,255,255])

        #higher range RED
        lowerRed2 = np.array([170, 120, 70])
        upperRed2 = np.array([180, 255,255])

        mask1 = cv.inRange(hsv, lowerRed1, upperRed1)
        mask2 = cv.inRange(hsv, lowerRed2, upperRed2)
        mask = mask1 + mask2


        #Gauasian blur
        blur = cv.GaussianBlur(mask, (5,5), 0)

        #gthresh
        _, thresh = cv.threshold(blur, 180, 255, cv.THRESH_BINARY)

        #canny edge detction
      
        kernal = cv.getStructuringElement(cv.MORPH_RECT, (7,7))
        closing = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernal)

        return closing, frame2, mask

  

    def stop(self):
        self.isRunning = False
        #halt the main thread so that the second thread we created stops before it executes again
        self.thread.join()
        self.cam.release()


    ###########################
    ####Lane Detection ########
    ###########################
    def centroidCalculations(self, processedFrame, displayFrame):
        #get countours in proceed image
        contours, heirarchy = cv.findContours(processedFrame, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)


        tuningNumber = 300


        foundCanny = 1
        for x in contours:
            
            if cv.contourArea(x) > tuningNumber:
                print(f"Large Canny found: ", foundCanny)
                foundCanny +=1

        centroids = []
        #show contour centroids
        for i in contours:
            if cv.contourArea(i) > tuningNumber:
                M = cv.moments(i)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/ M['m00'])
                    cv.drawContours(displayFrame, [i], -1, (0,255,0), 2)
                    cv.circle(displayFrame, (cx,cy), 7, (0,255,255), -1)
                    appending = [cx,cy]
                    centroids.append(appending)
                    print(f"Controid at x: {cx} y: {cy}")

        midpointX = None
        midpointY = None
                    
        #find centroids midpoint
        for i in range(len(centroids) - 1):
            cx1,cy1 = centroids[i]
            cx2,cy2  = centroids[i+1]
            midpointX = int((cx2 + cx1) / 2)
            midpointY = int((cy2+cy1) / 2)
            cv.circle(displayFrame, (midpointX,midpointY), 7, (0,0,255), -1)



        return midpointX, midpointY
        #loop and calcuatie centroid for each one
        



################################################################################################################################################################################################
################################ MAINLOOP MAINLOOP MAINLOOP MAINLOOP MAINLOOP ##################################################################################################################
################################################################################################################################################################################################


#Instantiating the class
manager = CamManage()

#null checks
if not manager.cam.isOpened():
    print("Camera not connected")
    exit()

manager.start() #starts running the new thread

#PID SETUP




while True:
    frame = manager.read()
    
    #redo the loop unitl frame is captured
    if frame is None:
        continue 


    #for display
    displayFrame = frame.copy()

    #optimiser
    processedFrame, displayFrame, maskFrame  = manager.preProcessing(frame)

    #Find midpoints
    midpointX, midpointY = manager.centroidCalculations(processedFrame, displayFrame)


   
    
    #display
    cv.imshow("Processed Video", processedFrame)
    cv.imshow("Original Video", displayFrame)
    cv.imshow("Mask", maskFrame)
    #exit
    exitKey= cv.waitKey(1)
    idle = "F"
    if exitKey == ord('l'):
        break
    
#exit sequence
manager.stop() #automatically releases the cameras
cv.destroyAllWindows()