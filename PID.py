import time







class PIDController():
    def __init__(self, Kp, Ki, Kd, setpoint):
        #tuning parameytrers
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        #stater variables
        self.setpoint = setpoint
        self.previousError = 0
        self.integral = 0
    def update(self, processVariable, dt):
        #calucate erroir
        error = self.setpoint - processVariable
        #calucate proportional term
        P = self.Kp * error
        #calculate integral term
        self.integral += error * dt #acculametale integral adn keep it time consistant
        I = self.Ki * self.integral
        #calculate derivitve term
        derivitive = (error-self.previousError) / dt
        D = self.Kd * derivitive
        #compute output
        output = P + I + D
        #update error
        self.previousError = error
        return output


pid = PIDController(Kp = 1.1, Ki = 0.1, Kd = 0.5, setpoint= 100)

#MAIN LOOP

##add a timer soi it only runs for so long before storing everyting in an array and plotting values 
currentValue = 180

while True:
    dt = 0.1


    measurement = currentValue

  
    #get pid output (aka the correction)
    _update =pid.update(currentValue, dt)

    #update currentBalue and siomluate process dynamincs
    currentValue += _update * 0.1 #0.1 reduces agressive overcorrections

    #print simulatiVn
    print(f"Setpoint is: {pid.setpoint} ||| CurrentValue: {currentValue:.2f} ||| Correction: {_update:.2f}")
    #sleep so it dosn'et constatnly poll
    time.sleep(dt)
