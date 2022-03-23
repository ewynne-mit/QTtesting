# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 22:04:36 2022

@author: hanla
"""
import pyfirmata

from pymeasure.instruments.keithley import Keithley2400
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time
import pandas as pd
import default_vals as df

arduino_port = 'COM4'
arduino = pyfirmata.Arduino('COM4')
for i in range(10):
    arduino.digital[i+2].write(0)
arduino.sp.close()



class KeithleyWorker(QObject):
    
    
    finished = pyqtSignal()
    intReady = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super(KeithleyWorker, self).__init__(parent)
        self.GPIB_address = df.default_GPIB
        self.pumpchannel = df.default_pumpchannel
        self.airchannel = df.default_airchannel
        self.valvechannel = df.default_valvechannel
        self.filename = df.default_filename

        self.voltage = df.default_voltage
        self.vstep = df.default_vstep
        self.steptime = df.default_steptime
        self.duration = df.default_duration
        self.extractiontime = df.default_extractiontime
        
        #sourcemeter starts undefined. must be created by prepareSource method
        self.sourcemeter = None
    
    @pyqtSlot()
    def procCounter(self):
        self.startArduino()
        self.sourcemeter.enable_source()
        
        self.sourcemeter.triad(600,0.05)
        for i in range(0,int(self.voltage+self.vstep),int(self.vstep)):
            #self.sourcemeter.ramp_to_voltage(i)
            self.sourcemeter.source_voltage = i
            self.intReady.emit(self.sourcemeter.current)
            time.sleep(self.steptime)
            
        self.sourcemeter.beep(3000,0.1)
        
        timeout_start = time.time()
        
            
        
        
        while time.time() < (timeout_start + self.duration*60):
            self.intReady.emit(self.sourcemeter.current)
            time.sleep(1)
            
         #for i in range(int(self.duration*60)):
             #self.intReady.emit(self.sourcemeter.current)
             #time.sleep(self.steptime)   
            
        self.extractArduino()
            
        self.sourcemeter.ramp_to_voltage(0)
        time.sleep(1)
        self.sourcemeter.disable_source()
        
        
        
        self.finished.emit()
    
    def setArduino(self, airchannel, pumpchannel, valvechannel):
        self.pumpchannel = pumpchannel
        self.airchannel = airchannel
        self.valvechannel = valvechannel
        
        
    def setKeithley(self, GPIB_address=df.default_GPIB, voltage=df.default_voltage, vstep=df.default_vstep, steptime=df.default_steptime,
                         duration=df.default_duration,extractiontime = df.default_extractiontime):
        self.GPIB_address = GPIB_address
        self.voltage = voltage
        self.vstep = vstep
        self.steptime = steptime
        self.duration = duration
        self.extractiontime = extractiontime
        
        self.sourcemeter = Keithley2400("GPIB::"+str(self.GPIB_address))
        self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.apply_voltage()
        self.sourcemeter.enable_source()
        self.sourcemeter.measure_current()
        self.sourcemeter.source_voltage = 0
        time.sleep(0.1)
        self.sourcemeter.disable_source()
        
    
    
    def startArduino(self):
        arduino.sp.open()
        time.sleep(2)
        arduino.digital[self.pumpchannel].write(1)
        time.sleep(2)
        arduino.digital[self.pumpchannel].write(0)
        #sleep(1)
        arduino.sp.close()
        
        return True
    
    def extractArduino(self):
        arduino.sp.open()
        time.sleep(2)
        arduino.digital[self.pumpchannel].write(1)
        time.sleep(2)
        arduino.digital[self.pumpchannel].write(0)
        
        arduino.digital[self.valvechannel].write(1)
        arduino.digital[self.airchannel].write(1)
        time.sleep(self.extractiontime)
        arduino.digital[self.valvechannel].write(0)
        arduino.digital[self.airchannel].write(0)
        arduino.sp.close()
        
        return True

    def stopArduino(self):
        arduino.sp.open()
        time.sleep(2)
        arduino.digital[self.airchannel].write(0)
        arduino.digital[self.valvechannel].write(0)
        arduino.digital[self.pumpchannel].write(1)
        time.sleep(2)
        arduino.digital[self.pumpchannel].write(0)
        #sleep(1)
        arduino.sp.close()
        return True