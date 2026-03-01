#import cv library and assign to variable cv
import cv2 as cv
 
cam = cv.VideoCapture(0)

#Null checks
if not cam.isOpened():
    print("Error: Canmera not connected")
    exit()

while True:
    #Capture each frame and return information (retrn)
    retrn, frame = cam.read()

    
    #---------optimisation  code go here __________#

    #display
    cv.imshow('Video',frame)
    #exit
    exitKey= cv.waitKey(1)
    if exitKey == ord('l'):
        break
    
#exit sequence
cv.release()
cv.destroyAllWindows()