#import cv library and assign to variable cv
import cv2 as cv
import threading
import numpy as np

#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self, camInt=0, width = 640, height =480):    
        self.cam = cv.VideoCapture(0)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        #---------Threading shared variables __________#

        self.frame = None #Stores captured frame and starts empty becuase no captured frame
        self.isRunning = False  #Thread loop running controls
        self.RCP = threading.Lock() #RCP is race condition prevention
      
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

    #frame processing
    def preProcessing(self, frame):
        #graysacle
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        #CLAHE
        clahe = cv.createCLAHE(clipLimit = 1.2, tileGridSize = (8,8))
        equalize = clahe.apply(gray)


        
        #Gauasian blur
        blur = cv.GaussianBlur(equalize, (5,5), 0)

        #Adaptive gausian threshold
        #Parameters: Inputframe, pixelMaxValue (white), threshMethod, threshType (Binary), maximum neighborhood area, noise reductioun constant
        gThresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

        #canny edge detction
        edges = cv.Canny(gThresh, 50,150)

        #morphological transformations
        kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5)) #create 5,5 ellipse kernal

        closing = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernal)
        opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernal)

        median = cv.medianBlur(opening, 5)

        #Hugh tranform
        #Parameters: Input, distancel resuliton, angle resultionms radians, line confidence, line segment lengjh, segment distance between eachother
        #smaller lines = smaller minlinelenght, noisy edges = increase threshold
        hugh = cv.HoughLinesP(median, rho = 1, theta=np.pi/180, threshold =50, minLineLength = 40, maxLineGap = 20)

        #draw lines
        if hugh is not None:
            for line in hugh:
                x1, y1, x2, y2 = line [0]
                cv.line(hugh, (x1,y1), (x2,y2), (0,255,0),2) 

        


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
manager.stop() #automatically releases the camera
cv.destroyAllWindows()