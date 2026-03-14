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

        #closgin pening
        kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE, (10,10))
        closing = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernal, iterations = 3)

        return closing
    
    def centroid(self, img):
        

        #get countours in proceed image
        contours, heirarchy = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

        print (str(len(contours)))
        for i in contours:
            M = cv.moments(i)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/ M['m00'])
                cv.drawContours(img, [i], -1, (0,255,0), 2)
                cv.circle(img, (cx,cy), 7, (0,255,255), -1)
            print(f"x: {cx} y: {cy}")

        #loop and calcuatie centroid for each one
        



#Instantiating the class
manager = CamManage()


#optimiser
img = manager.preProcessing()

#display
cv.imshow("video1", img)
manager.centroid(img)

#exit
exitKey= cv.waitKey(1)



while True: 
    if exitKey == ord('l'):
        cv.destroyAllWindows()
        break
#exit sequence
