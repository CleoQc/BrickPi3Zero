
from BrickPi import *

print TYPE_SENSOR_EV3_COLOR_M3

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
                     TYPE_SENSOR_EV3_COLOR_M4  # 54 -> Raw Color Components
                    ]

    nxt_color_mode = [
                      TYPE_SENSOR_COLOR_FULL, # 36 
                      TYPE_SENSOR_COLOR_RED,  # 37 red LED in the sensor
                      TYPE_SENSOR_COLOR_GREEN,# 38 green LED 
                      TYPE_SENSOR_COLOR_BLUE, # 39 blue LED 
                      TYPE_SENSOR_COLOR_NONE, # 40 no LED 
                     ]

    sensor_type = ["NXT","EV3"]
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

        debug(" creating Color Sensor on port {}".format(in_port))
        self.current_mode = None

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


    def set_color_mode(self):
        """
        sets the sensor to read in colors

        usage:
        sensor type must be defined first (done at init() time)
        
        Exception:
        raises a ValueError if sensor_type is undefined

        """
        if self.type == "EV3":
            self.mode = TYPE_SENSOR_EV3_COLOR_M2
        elif self.type=="NXT":
            self.mode = TYPE_SENSOR_COLOR_FULL
        else:
            raise ValueError("Unknown sensor type")


    def set_light_mode(self):
        """
        Sets the sensor to detect reflected light levels
        """
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

if __name__ == "__main__":
    try:
        ev3colorsensor = BrickPiColorSensor("NXT",PORT_1)
        nxtcolorsensor = BrickPiColorSensor("EV3",PORT_3)
    except ValueError as e:
        print("wrong port {}".format(repr(e)))

    try:
        ev3colorsensor.set_color_mode()
        nxtcolorsensor.set_color_mode()
    except Exception as e:
        print("oops {}".format(repr(e)))
    
    (modestr,mode)= ev3colorsensor.get_current_mode()
    print modestr
    

