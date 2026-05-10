#import cv library and assign to variable cv
import cv2 as cv
import threading
import numpy as np

###PID ENCAPSULATION ClASS #####
#______________________________#
import time





class PIDController():
    def __init__(self, Kp, Ki, Kd, setpoint):
        #tuning parameytrers
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        #stater variables
        self.setpoint = setpoint
        self.previousError = 0
        


        #integral 
        self.integral = 0
        self.integralMin = -50
        self.integralMax = 50
        
        #Derivitive
        self.derivitive = 0
        self.lpf = 0.8 #low pass filter



    def update(self, processVariable, dt):
        #calucate erroir
        error = self.setpoint - processVariable

        #calucate proportional term
        P = self.Kp * error

        #calculate integral term
        self.integral += error * dt #acculametale integral adn keep it time consistant
        self.integral = max(self.integralMin, min(self.integral, self.integralMax)) #clamping
        I = self.Ki * self.integral


        #calculate derivitve term
        rawDerivitive = (error-self.previousError) / dt
        self.derivitive = (self.lpf * self.derivitive) + ((1-self.lpf) * rawDerivitive)
        D = self.Kd * self.derivitive

        #compute output
        output = P + I + D

        #update error
        self.previousError = error
        return output



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

            [0,0], #top left
            [320,0], #top right
            [320,320], #bottom right
            [0,320]   #bottom left
            ])

        self.dstPoints = np.float32([ #destination points muilti dimenstional array

            [100,50], #top left
            [220,50], #top right
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
    def TopDownView(self,frame, ):
        warped = cv.warpPerspective(frame, self.HM, (320, 240))
        return warped

    def frame2(self, frame):
        frameTwo = self.TopDownView(frame)
        return frameTwo
    
    #frame processing
    def preProcessing(self, frame):

        #birds eye view
        frame = self.TopDownView(frame)
        frame2 = self.TopDownView(frame)

        
        #graysacle
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        #Gauasian blur
        blur = cv.GaussianBlur(gray, (5,5), 0)

        #gthresh
        gThresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY , 11,2)

        #canny edge detction
        edges = cv.Canny(gThresh, 50,150)
      
        kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2,2))
        closing = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernal)

        return closing, frame2

  

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

        foundCanny = 1
        for x in contours:
            
            if cv.contourArea(x) > 100:
                print(f"Large Canny found: ", foundCanny)
                foundCanny +=1

        centroids = []
        #show contour centroids
        for i in contours:
            if cv.contourArea(i) > 100:
                M = cv.moments(i)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/ M['m00'])
                    cv.drawContours(displayFrame, [i], -1, (0,255,0), 2)
                    cv.circle(displayFrame, (cx,cy), 7, (0,255,255), -1)
                    appending = [cx,cy]
                    centroids.append(appending)
                    print(f"Controid at x: {cx} y: {cy}")
                    
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

frameCenter = 160

pid = PIDController( Kp=0.6, Ki = 0.01, Kd=0.2, setpoint= frameCenter)

prevTime = time.time()

#serial setuip here

while True:
    frame = manager.read()
    
    #redo the loop unitl frame is captured
    if frame is None:
        continue 


    #for display
    displayFrame = frame.copy()

    #optimiser
    frame  = manager.preProcessing(frame)

    #Find midpoints
    midpointX, midpointY = manager.centroidCalculations(frame, displayFrame)

    #PID calc
    currentTime = time.time()
    dt = currentTime - prevTime
    prevTime = currentTime

    if midpointX is not None:
        correction = pid.update(midpointX, dt)
        print(correction)
    
    #display
    cv.imshow("Processed Video", frame)
    cv.imshow("Original Video", displayFrame)
    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
manager.stop() #automatically releases the cameras
cv.destroyAllWindows()