import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)

#Arduno rest time
time.sleep(2)

tempList = ["F", "L", "R", "I"]
while True:
    #send message
    for i in tempList:
        message = i
        ser.write(message.encode('utf-8')) 
        print("Sent: ", message.strip())
        time.sleep(2)

    #recieveing from arduino
    while ser.in_waiting: 
        line = ser.readline().decode('utf-8').strip()
        print(R"Recieved: ", line)
        
   