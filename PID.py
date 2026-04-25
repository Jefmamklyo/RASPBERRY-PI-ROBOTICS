import time
import numpy as np
import matplotlib.pyplot as plt





class PIDController():
    def __init__(self, Kp, Ki, Kd, setpoint):
        #tuning parameytrers
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        #stater variables
        self.setpoint = setpoint
        self.previousError = 0
        


        #integral 
        self.integral = 0
        self.integralMin = -50
        self.integralMax = 50
        
        #Derivitive
        self.derivitive = 0
        self.lpf = 0.8 #low pass filter



    def update(self, processVariable, dt):
        #calucate erroir
        error = self.setpoint - processVariable

        #calucate proportional term
        P = self.Kp * error

        #calculate integral term
        self.integral += error * dt #acculametale integral adn keep it time consistant
        self.integral = max(self.integralMin, min(self.integral, self.integralMax)) #clamping
        I = self.Ki * self.integral


        #calculate derivitve term
        rawDerivitive = (error-self.previousError) / dt
        self.derivitive = (self.lpf * self.derivitive) + ((1-self.lpf) * rawDerivitive)
        D = self.Kd * self.derivitive

        #compute output
        output = P + I + D

        #update error
        self.previousError = error
        return output


setpoint = 100

pid = PIDController(Kp = 1.1, Ki = 0.1, Kd = 0.5, setpoint= setpoint)

#MAIN LOOP

##add a timer soi it only runs for so long before storing everyting in an array and plotting values 
currentValue = 180
#simulate parameters

time = np.linspace(0,30,100) #10 sec, 100 steps
dt = time[1] - time[0]

#list for ploitting
values = []

for t in time:


    measurement = currentValue

  
    #get pid output (aka the correction)
    _update =pid.update(currentValue, dt)

    #update currentBalue and siomluate process dynamincs
    currentValue += _update * 0.1 #0.1 reduces agressive overcorrections

    #print simulatiVn
    print(f"Setpoint is: {pid.setpoint} ||| CurrentValue: {currentValue:.2f} ||| Correction: {_update:.2f}")

    values.append(currentValue)

#plotting results
plt.figure(figsize = (10,6))
plt.plot(time, values, label = "values (currentValue)")
plt.axhline(y = setpoint, color = 'r', linestyle = '--', label ='Setpoint' )
plt.xlabel('Time (s)')
plt.ylabel("currentValue") 
plt.title("PID Graph. Correction over time")
plt.legend()
plt.grid()
plt.show()
