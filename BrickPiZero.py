import time
from threading import Thread
from BrickPi import *

def debug(in_str):
    print(in_str)
    pass



#################################################
# Base sensor class
#################################################
class BrickPiSensor():
    '''
    Base class

    members: 
    port = which port the sensor is on
    type = NXT vs EV3, str must be in sensor_type array
    mode = this determines which sensor and which sensor mode are activated
    descriptor = string to describe the sensor for printing purposes
    '''
    #################################################
    # Threading class
    #################################################
    class BrickPiThread(Thread):
        '''
        Run one Thread that keeps updating the sensors
        '''
        def __init__(self, threadID, name, counter):
            Thread.__init__(self)
            debug("starting thread")
            self.threadID = threadID
            self.name = name
            self.counter = counter

        def run(self):
            debug ("starting run")
            while True:
                while self.threading_is_needed:
                    try:
                        BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
                        time.sleep(.2)              # sleep for 200 ms
                    except:
                        pass
                pass

        # def __enter__(self):
        #     return self

        # def __exit__(self):
        #     BrickPiUpdateValues()

    sensor_type = ["NXT","EV3"]
    start_thread = False
    threading_is_needed = True

    if start_thread is False:
        print("starting thread")
        update_thread = BrickPiThread(1, "MotorThread",1)
        update_thread.setDaemon(True)
        update_thread.start()
        update_thread.threading_is_needed = False
        start_thread = True

    def __init__(self,in_type,in_port):
        """
        initiate the sensor

        args:
        in_port: port number, between 0 and 3. Fails otherwise
        in_type: "NXT" or "EV3". Fails otherwise

        return values:
        none

        Exceptions:
        raises a ValueError if in_type is unknown
        raises a ValueError if in_port is not between 0 and 3
        """
        BrickPiSetup()

        self.descriptor = "unknown sensor"

        if in_port >= 0 and in_port <= 3:
            self.port = in_port
        else:
            self.port = -1
            raise ValueError("Invalid port number: {}".format(in_port))

        if in_type in self.sensor_type:
            self.type = in_type
        else:
            self.type= ""
            raise ValueError("Unknown sensor type: %s"%str(in_type))

    def __str__(self):
        '''
        used for debugging purposes
        prints out a nicely formatted sensor identification string
        each class that inherits from this base class is expected to set
            self.descriptor to a nice string
        '''
        return str(self.type)+" "+self.descriptor+" sensor on "+str(self.port+1)

    def suspend_updates(self):
        self.update_thread.threading_is_needed  = False

    def restart_updates(self):
        self.update_thread.threading_is_needed = True

    def set_mode(self,in_mode):
        '''
        NOTA: set_mode makes a call to BrickPiSetupSensors() which may have 
        a long delay (up to 5 seconds)
        DO NOT ABUSE
        '''
        self.mode = in_mode
        BrickPi.SensorType[self.port] = in_mode
        BrickPiSetupSensors()

#################################################
# BrickPiMotor
#################################################

class BrickPiMotor(BrickPiSensor):
    def __init__(self,in_type,in_port):
        BrickPiSensor.__init__(self,in_type,in_port)
        self.power = 0
        self.descriptor = "motor"
        BrickPi.MotorEnable[self.port] = 1
        
        self.set_power(200) # set default power
        #debug ("Creating a {} on port {}".format(self.descriptor,self.port))

    def __str__(self):
        return "{} at {} power ".format(self.descriptor,self.power)

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.power=0


    def set_power(self,in_power=200):
        '''
        power must be between -255 and 254 and be an integer
        power is assumed to be positive but can very well be negative
            if power is negative go_backwards will actually go forward
        We keep track of the required power but we don't transfer it yet to
        the firmware. 
            The transfer will be done when movement is actually required

        '''
        try:
            self.power = int(in_power)
        except:
            raise ValueError("Power must be an integer between -255 and 254")
        if self.power > 254 or self.power < -255:
            raise ValueError("Power must be an integer between -255 and 254")

    def get_power(self):
        return self.power

    def go_forward(self,secs=0):
        '''
        if you provide a value for secs other than 0, this call
        becomes blocking.
        If you don't provide a value, you are responsible to stop
        the motor whenever you want
        '''
        try:
            BrickPi.MotorSpeed[self.port] = self.power 
        except ValueError:
            raise ValueError("Motor does not have a valid power setting")
        if secs > 0:
            time.sleep(secs)    

    def go_backward(self,secs=0):
        '''
        will reverse the power for this call
        self.power will stay the same value ready for another use
        '''
        try:
            BrickPi.MotorSpeed[self.port] = -self.power 
        except:
            raise ValueError("Motor does not have a valid power setting")
        if secs > 0:
            time.sleep(secs)    

    def stop(self,coast=False):
        BrickPi.MotorSpeed[self.port]=0
        if coast is False:
            BrickPiUpdateValues()

    def coast(self):
        self.stop(coast=True)

#################################################
# brickpimotors
#################################################

class BrickPiMotors():
    def __init__(self,motors):
        '''
        motors is an array that contains BrickPiMotor names
        ''' 
        self.motors = []
        for i in range(len(motors)):
            self.motors.append(motors[i])

    def __str__(self):
        outstr = ""
        for i in range(len(self.motors)):
            outstr = outstr + str(self.motors[i])+"\n"
        return outstr

    def go_forward(self,in_secs=0, in_coast=False):
        '''
        in_secs = how long should motors go forward 
                 if non zero, this is blocking
        in_stop = what kind of stopping is requested, 
                  True is hard stop, False is coasting
        '''
        self.motors[0].suspend_updates()
        for i in range(len(self.motors)):
            self.motors[i].go_forward()
        self.motors[0].restart_updates()
        if in_secs > 0:
            time.sleep(in_secs)
            debug ("done with sleep")
        self.stop(in_coast)


    def go_backward(self,in_secs=0, in_coast=True):
        '''
        in_secs = how long should motors go forward 
                 if non zero, this is blocking
        in_stop = what kind of stopping is requested, 
                  True is hard stop, False is coasting
        '''
        for i in range(len(self.motors)):
            self.motors[i].go_backward()
        if in_secs > 0:
            time.sleep(secs)
        self.stop(in_coast)

    def stop(self,in_coast=False):
        for i in range(len(self.motors)):
            self.motors[i].stop(in_coast)

#################################################
# BrickPi Color Sensor
#################################################

class BrickPiColorSensor(BrickPiSensor):
    """
    BrickPi Color Sensor 
    """
    ev3_color_mode = [TYPE_SENSOR_EV3_COLOR_M0, # 50 -> Reflected light mode
                     TYPE_SENSOR_EV3_COLOR_M1,  # 51 -> Ambient light mode
                     TYPE_SENSOR_EV3_COLOR_M2,  # 52 -> Color mode
                     TYPE_SENSOR_EV3_COLOR_M3,  # 53 -> Raw reflected light mode
                     TYPE_SENSOR_EV3_COLOR_M4,  # 54 -> Raw Color Components
                    ]
    nxt_color_mode = [TYPE_SENSOR_COLOR_FULL, # 36 
                     TYPE_SENSOR_COLOR_RED,  # 37 red LED in the sensor
                     TYPE_SENSOR_COLOR_GREEN,# 38 green LED 
                     TYPE_SENSOR_COLOR_BLUE, # 39 blue LED 
                     TYPE_SENSOR_COLOR_NONE, # 40 no LED 
                     TYPE_SENSOR_LIGHT_OFF,  # 0 Light sensor off 
                     TYPE_SENSOR_LIGHT_ON,   # Light sensor on 
                     ]

    colors = ["None","Black","Blue","Green","Yellow","Red","White","Brown"]


    # dictionary to be able to offer a kid-readable string about the sensor mode
    sensor_modes = {
                TYPE_SENSOR_EV3_COLOR_M0:"EV3 Reflected light mode",
                TYPE_SENSOR_EV3_COLOR_M1:"EV3 Ambient light mode",
                TYPE_SENSOR_EV3_COLOR_M2:"EV3 Color mode",
                TYPE_SENSOR_EV3_COLOR_M3:"EV3 Raw reflected light mode",
                TYPE_SENSOR_EV3_COLOR_M4:"EV3 Raw color mode",
                TYPE_SENSOR_COLOR_FULL:"NXT color mode",
                TYPE_SENSOR_COLOR_RED:"NXT Red mode",
                TYPE_SENSOR_COLOR_GREEN:"NXT Green mode",
                TYPE_SENSOR_COLOR_BLUE:"NXT Blue mode",
                TYPE_SENSOR_COLOR_NONE:"NXT off mode"
                    }

    def __init__(self,in_type,in_port):
        """
        initiate the sensor

        args:
        in_port: port number, between 0 and 3. Fails otherwise
        in_type: "NXT" or "EV3". Fails otherwise

        return values:
        none

        Exceptions inherited from base class:
        raises a ValueError if in_type is unknown
        """
        #debug(" creating Color Sensor on port {}".format(in_port))
        BrickPiSensor.__init__(self,in_type,in_port)

        self.descriptor = "color"

        if in_type is "NXT":
            self.mode = TYPE_SENSOR_COLOR_FULL
        else:   
            self.mode = TYPE_SENSOR_EV3_COLOR_M2

    def __enter__(self):
        '''
        starts a context manager (to be used with a with statement)
        '''
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.set_mode(TYPE_SENSOR_COLOR_NONE)
        BrickPiUpdateValues()

    def read():
        '''
        reads the color sensor

        args: none
        returns: string describing the color
        '''
        if result is 0: # no errors
            #debug("Port: {}".format(self.port+1))
            #debug("Sensor Reading: {}".format(BrickPi.Sensor[self.port]))
            if BrickPi.Sensor[self.port]<8:
                #debug( "Color is: {}".format(self.colors[BrickPi.Sensor[self.port] ]))
                return self.colors[BrickPi.Sensor[self.port] ]
        return("Error in reading color sensor")

    def set_color_mode(self):
        """
        sets the sensor to read colors

        usage:
        sensor type must be defined first (done at init() time)
        
        Exception:
        raises a ValueError if sensor_type is undefined

        """
        if self.type == "EV3":
            self.set_mode(TYPE_SENSOR_EV3_COLOR_M2)
        elif self.type=="NXT":
            self.set_mode (TYPE_SENSOR_COLOR_FULL)
        else:
            raise ValueError("Unknown sensor type")
            return
        #debug("Mode {1} on port {0}".format(self.port,self.mode))


    def set_reflected_light_mode(self):
        """
        Sets the sensor to detect reflected light levels
        """
        if self.type == "EV3":
            self.set_mode(TYPE_SENSOR_EV3_COLOR_M0)
        elif self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_LIGHT_ON)
        pass

    def set_ambient_light_mode(self):
        pass

    def get_current_mode(self):
        """
        Returns current mode for the sensor

        Args: none

        Return:
        tuple : first item is a string descriptor
                second item is the ID
        """

        return self.sensor_modes[self.mode],self.mode

    def set_next_color_lamp(self):
        if self.type=="NXT":
            #debug("self.mode: {}".format(self.mode))
            new_mode = self.mode+1 if self.mode < 40 else 37
            #debug("New mode:{}".format(new_mode))
            self.set_mode(new_mode)

    def set_green_lamp(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_GREEN)
            #debug("Green lamp")
        else:
            raise ValueError("Not an NXT color sensor")

    def set_red_lamp(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_RED)
            #debug("Red lamp")
        else:
            raise ValueError("Not an NXT color sensor")

    def set_blue_lamp(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_BLUE)
            #debug("Blue lamp")
        else:
            raise ValueError("Not an NXT color sensor")

    def set_lamp_off(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_NONE)
            #debug("Lamp off")
        else:
            raise ValueError("Not an NXT color sensor")

    def wait_for_color(self,color):
        pass



























##################################################################
##################################################################
# EXAMPLE CODE FOR EACH CLASS
##################################################################
##################################################################

def colorcycle():
    '''
    Cycles through three colors with for loop
    '''
    colorsensor = BrickPiColorSensor("NXT",PORT_1)
    colorsensor.set_red_lamp()
    for i in range(10):
        time.sleep(1)
        colorsensor.set_next_color_lamp()


def colorcycle2():
    '''
    Cycles through three colors with 'with' statement
    '''
    with BrickPiColorSensor("NXT",PORT_1) as colorsensor:
        print colorsensor
        colorsensor.set_red_lamp()
        for i in range(10):
            colorsensor.set_next_color_lamp()
            time.sleep(1)

def ev3color():
    colorsensor = BrickPiColorSensor("EV3",PORT_4)
    colorsensor.set_color_mode()
    for i in range(4):
        color = colorsensor.read()
        print "color: ",color
        time.sleep(1)

def motorhandling():
    motor1 = BrickPiMotor("NXT",PORT_A)
    motor1.go_forward()
    time.sleep(1)
    motor1.set_power(20)
    motor1.go_backward()
    time.sleep(5)
    motor1.coast()

def carhandling():
    motor1 = BrickPiMotor("NXT",PORT_A)
    motor2 = BrickPiMotor("NXT",PORT_C)
    propulsion = BrickPiMotors([motor1,motor2])
    print( propulsion)
    propulsion.go_forward(secs=5)
    propulsion.go_backward()
    time.sleep(1)
    propulsion.stop()

def doubleduty():
    motor1 = BrickPiMotor("NXT",PORT_A)
    motor2 = BrickPiMotor("NXT",PORT_C)
    propulsion = BrickPiMotors([motor1,motor2])
    colorsensor = BrickPiColorSensor("NXT",PORT_1)
    propulsion.go_forward(in_secs=5)
    colorsensor.set_red_lamp()
    motor1.go_forward()
    for i in range(10):
        time.sleep(1)
        colorsensor.set_next_color_lamp()
    motor1.stop()
    colorsensor.set_lamp_off()

if __name__ == "__main__":
    #colorcycle()
    #colorcycle2()
    #ev3color()
    #carhandling()
    #motorhandling()
    doubleduty()
