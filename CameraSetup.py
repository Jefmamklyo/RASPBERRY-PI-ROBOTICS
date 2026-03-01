#import cv library and assign to variable cv
import cv2 as cv

#Define camera
cam = cv.VideoCapture(0)
#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self, camInt=0, width = 640, height =480):    
        self.setting = (width,height)
    
    #Setting/Further optimisation
    def setting(self,width,height):
        cam.resize(frame(width,height))
         #---------optimisation  code go here __________#


while True:
    #Capture each frame and return information (retrn)
    retrn, frame = cam.read()

    
    CamManage.setting

    #display
    cv.imshow('Video',frame)
    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
cv.release()
cv.destroyAllWindows()