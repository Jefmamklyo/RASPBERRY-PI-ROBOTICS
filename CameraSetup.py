#import cv library and assign to variable cv
import cv2 as cv
import threading
import numpy as np

#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self, camInt=0, width = 320, height =240):    
        self.cam = cv.VideoCapture(camInt, cv.CAP_V4L2)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        #---------Threading shared variables __________#

        self.frame = None #Stores captured frame and starts empty becuase no captured frame
        self.isRunning = False  #Thread loop running controls
        self.RCP = threading.Lock() #RCP is race condition prevention

        #__________________Homography Matricies_______________#

        self.srcPoints = np.float32([  #source points muilti dimenstional array

            [100,140], #top left
            [220, 140], #top right
            [300,220], #bottom left
            [20,220]   #bottom right
            ])

        self.dstPoints = np.float32([ #destination points muilti dimenstional array

            [0,0], #bottom left
            [320,0], #bottom right
            [320,240], #top left
            [0,240]    #top right   
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


    #frame processing
    def preProcessing(self, frame):

        #birds eye view
        frame = self.TopDownView(frame)
        #graysacle
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        #CLAHE
        clahe = cv.createCLAHE(clipLimit = 1.2, tileGridSize = (8,8))
        equalize = clahe.apply(gray)

        #Gauasian blur
        blur = cv.GaussianBlur(equalize, (5,5), 0)

        #gthresh
        gThresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11,2)

        #canny edge detction
        edges = cv.Canny(gThresh, 30,120)
      
        kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
        closing = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernal)
        opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernal)
        median = cv.medianBlur(opening, 5)

        return frame


    def stop(self):
        self.isRunning = False
        #halt the main thread so that the second thread we created stops before it executes again
        self.thread.join()
        self.cam.release()



#Instantiating the class
manager = CamManage()

#null checks
if not manager.cam.isOpened():
    print("Camera not connected")
    exit()

manager.start() #starts running the new thread


#Main thread
while True:
    frame = manager.read()

    
    #redo the loop unitl frame is captured
    if frame is None:
        continue 

    #optimiser
    frame2 = manager.preProcessing(frame)
    
    #display
    cv.imshow("video1", frame)
    cv.imshow('Video', frame2)
    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
manager.stop() #automatically releases the cameras
cv.destroyAllWindows()