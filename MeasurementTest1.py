#import packages
from pymeasure.instruments.keithley import Keithley2400
import numpy as np
import pandas as pd
from time import sleep

def make_measurement(filename = "filename",GPIB_address=4, set_voltage=50.0, voltage_increment=2.0, timestep=1.0, duration=3.0):
    max_current = 0.1 #100 miliamps
    address = "GPIB::" + str(GPIB_address)
    sourcemeter = Keithley2400(address)
    sourcemeter.reset()
    sourcemeter.use_front_terminals()
    sourcemeter.measure_current()
    sourcemeter.apply_voltage(set_voltage,max_current)
    
