#import cv library and assign to variable cv
import cv2 as cv
import threading
import numpy as np

#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self):    
        self.img = cv.imread("/home/aakash/programming/PrototypeProject/Track-for-Autonomous-Lane-Detection-Car-2345030835.jpg")

 
    #frame processing
    def preProcessing(self):

        
        #graysacle
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)

        
        #Gauasian blur
        blur = cv.GaussianBlur(gray, (9,9), 0)

        #gthresh
        gThresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY , 11,2)

        #canny edge detction
        edges = cv.Canny(gThresh, 50,150)

        return edges

#Instantiating the class
manager = CamManage()



#Main thread
while True: 
    img = manager.img
  
    #optimiser
    img = manager.preProcessing()
    
    #display
    cv.imshow("video1", img)

    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
cv.destroyAllWindows()