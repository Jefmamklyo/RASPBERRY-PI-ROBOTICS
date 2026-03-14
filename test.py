#import cv library and assign to variable cv
import cv2 as cv
import threading
import numpy as np

#Encapsulation class
class CamManage:
    #Contructor 
    def __init__(self):    
        self.img = cv.imread("/home/aakash/programming/PrototypeProject/Track-for-Autonomous-Lane-Detection-Car-2345030835.jpg")
        self.originalImg =self.img.copy()

 
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
    
    def centroidCalculations(self, img):
        #get countours in proceed image
        contours, heirarchy = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

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
                    cv.drawContours(self.originalImg, [i], -1, (0,255,0), 2)
                    cv.circle(self.originalImg, (cx,cy), 7, (0,255,255), -1)
                    appending = [cx,cy]
                    centroids.append(appending)
                    print(f"Controid at x: {cx} y: {cy}")
                 
        #find centroids midpoint
        for i in range(len(centroids) - 1):
            cx1,cy1 = centroids[i]
            cx2,cy2  = centroids[i+1]
            midpointX = int((cx2 + cx1) / 2)
            midpointY = int((cy2+cy1) / 2)
            cv.circle(self.originalImg, (midpointX,midpointY), 7, (0,0,255), -1)



        cv.imshow("Controid img", self.originalImg)
        cv.waitKey(0)
        #loop and calcuatie centroid for each one
        



#Instantiating the class
manager = CamManage()



#optimiser
Pimg = manager.preProcessing()

#display
cv.imshow("video1", Pimg)
manager.centroidCalculations(Pimg)

#exit
exitKey= cv.waitKey(0)


if exitKey == ord('l'):
    cv.destroyAllWindows()
    
#exit sequence
