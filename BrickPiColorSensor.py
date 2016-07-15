import time
from BrickPi import *


def debug(in_str):
    print(in_str)
    pass

class BrickPiColorSensor():
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

    sensor_type = ["NXT","EV3"]

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

        Exceptions:
        raises a ValueError if in_type is unknown
        """
        BrickPiSetup()
        debug(" creating Color Sensor on port {}".format(in_port))
        self.mode = TYPE_SENSOR_COLOR_NONE

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


    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.set_mode(TYPE_SENSOR_COLOR_NONE)
        BrickPiSetupSensors()
        BrickPiUpdateValues()

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
        debug("Mode {1} on port {0}".format(self.port,self.mode))


    def set_mode(self,in_mode):
        self.mode = in_mode
        BrickPi.SensorType[self.port] = in_mode
        BrickPiSetupSensors()

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
            debug("self.mode: {}".format(self.mode))
            new_mode = self.mode+1 if self.mode < 40 else 37
            debug("New mode:{}".format(new_mode))
            self.set_mode(new_mode)
            BrickPiSetupSensors()
            BrickPiUpdateValues()

    def set_green_lamp(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_GREEN)
            BrickPiSetupSensors()
            BrickPiUpdateValues()
            debug("Green lamp")
        else:
            raise ValueError("Not an NXT color sensor")

    def set_red_lamp(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_RED)
            BrickPiSetupSensors()
            BrickPiUpdateValues()
            debug("Red lamp")
        else:
            raise ValueError("Not an NXT color sensor")

    def set_blue_lamp(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_BLUE)
            BrickPiSetupSensors()
            BrickPiUpdateValues()
            debug("Blue lamp")
        else:
            raise ValueError("Not an NXT color sensor")

    def set_lamp_off(self):
        if self.type=="NXT":
            self.set_mode ( TYPE_SENSOR_COLOR_NONE)
            BrickPiSetupSensors()
            BrickPiUpdateValues()
            debug("Lamp off")
        else:
            raise ValueError("Not an NXT color sensor")

    def read(self):
        """
        returns current color as a string

        args: None
    
        return: 
            the string associated with the color, taken from colors array
            the string "Error"  in case of issues
        """

        result = BrickPiUpdateValues()
        debug("Result: {}".format(result))
        if not result:
            debug("Port: {}".format(self.port+1))
            debug("Sensor Reading: {}".format(BrickPi.Sensor[self.port]))
            if BrickPi.Sensor[self.port]<8:
                debug( "Color is: {}".format(self.colors[BrickPi.Sensor[self.port] ]))
                return self.colors[BrickPi.Sensor[self.port] ]
        return("Error")


    def wait_for_color(self,color):
        pass

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
        colorsensor.set_red_lamp()
        for i in range(10):
            colorsensor.set_next_color_lamp()

def ev3color():
    colorsensor = BrickPiColorSensor("EV3",PORT_4)
    colorsensor.set_color_mode()
    for i in range(4):
        color = colorsensor.read()
        print "color: ",color
        time.sleep(1)

if __name__ == "__main__":
    #colorcycle()
    colorcycle2()
    #ev3color()
