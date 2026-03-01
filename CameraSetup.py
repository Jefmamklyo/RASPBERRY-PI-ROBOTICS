#import cv library and assign to variable cv
import cv2 as cv

#Define camera

#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self, camInt=0, width = 640, height =480):    
        self.cam = cv.VideoCapture(0)
        self.width = width
        self.height = height
    
    #Setting/Further optimisation
    def setting(self, frame):
        frame = cv.resize(frame, (self.width,self.height))
        frame =cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        return frame
         #---------optimisation  code go here __________


#Instantiating the class
manager = CamManage()

#null checks
if not manager.cam.isOpened():
    print("Camera not connected")
    exit()



while True:
    #Capture each frame and return information (retrn)
    retrn, frame = manager.cam.read()

    #Calling setting
    frame = manager.setting(frame)
    

    #display
    cv.imshow('Video',frame)
    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
cv.release()
cv.destroyAllWindows()