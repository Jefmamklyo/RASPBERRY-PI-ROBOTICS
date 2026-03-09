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

            [100,140], #bottom left
            [220,140], #bottom right
            [300,220], #top left
            [20,220]   #top right
            ])

        self.dstPoints = np.float32([ #destination points muilti dimenstional array

            [100,140], #bottom left
            [220,140], #bottom right
            [300,220], #top left
            [20,220]    #top right   
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

        #canny edge detction
        edges = cv.Canny(blur, 30,120)
      
        #Hugh tranform
        #Parameters: Input, distancel resuliton, angle resultionms radians, line confidence, line segment lengjh, segment distance between eachother
        #smaller lines = smaller minlinelenght, noisy edges = increase threshold
        lines = cv.HoughLinesP(edges, rho = 1, theta=np.pi/180, threshold =50, minLineLength = 60, maxLineGap = 5)

        #draw lines
      
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line [0]
                cv.line(frame,(x1,y1), (x2,y2), (0,255,0),2) 
            
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
    frame = manager.preProcessing(frame)
    
    #display
    cv.imshow('Video', frame)

    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
manager.stop() #automatically releases the cameras
cv.destroyAllWindows()