#import cv library and assign to variable cv
#Import threading
import cv2 as cv
import threading


#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self, camInt=0, width = 640, height =480):    
        self.cam = cv.VideoCapture(0)
        self.width = width
        self.height = height
        #---------Threading shared variables __________#

        self.frame = None #Stores captured frame and starts empty becuase no captured frame
        self.isRunning = False  #Thread loop running controls
      
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
                self.frame= frame
        
    #returnlatest frame stored in self.frame
    def read(self):
        return self.frame

    #frame processing
    def setting(self, frame):
        frame = cv.resize(frame, (self.width,self.height))
        frame =cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        return frame
         #---------optimisation  code go here __________

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

    #Optimiser
    optimiser = manager.setting(frame)
    
    #display
    cv.imshow('Video', optimiser)

    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
manager.stop() #automatically releases the camera
cv.destroyAllWindows()