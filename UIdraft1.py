import sys
import os
import serial


from pymeasure.instruments.keithley import Keithley2400
import numpy as np
import pandas as pd
from time import sleep
from random import randint

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
#import pyqtgraph.exporters
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QGridLayout, QDialog, \
    QDialogButtonBox

default_filename = 'file'
default_voltage = 50
default_vstep = 2
default_steptime = 1

default_duration = 0.1
default_flowrate = 0.1
default_extractiontime = 10

default_GPIB = 4
default_pumpchannel = 6
default_airchannel = 7
default_valvechannel = 8

arduino_port = '/dev/cu.usbmodem142301'
ser = serial.Serial(arduino_port, 9600, timeout=1)
ser.write(b'L')
x = 0



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #define variables
        self.GPIB_address = default_GPIB
        self.pumpchannel = default_pumpchannel
        self.airchannel = default_airchannel
        self.valvechannel = default_valvechannel

        self.voltage = default_voltage
        self.vstep = default_vstep
        self.steptime = default_steptime
        self.duration = default_duration
        self.extractiontime = default_extractiontime
        self.filename = default_filename

        self.setWindowTitle("HT-Concentrator UI")

        self.times = list(range(1))
        self.currents = list(range(1))

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.times, self.currents, pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()








        # define File naming Box
        self.file_entry_label = QLabel()
        self.file_entry_label.setText('Enter Filename')
        self.file_entry_label.setStyleSheet("background-color: darkGray")

        self.file_input = QLineEdit()
        self.file_input.setText(default_filename)

        # define Voltage Box
        self.voltage_entry_label = QLabel()
        self.voltage_entry_label.setText('Set Voltage [V]')
        self.voltage_entry_label.setStyleSheet("background-color: darkGray")

        self.voltage_input = QLineEdit()
        self.voltage_input.setText(str(default_voltage))

        # define Voltage Increment Box
        self.voltageinc_entry_label = QLabel()
        self.voltageinc_entry_label.setText('Set Voltage Increment [V]')
        self.voltageinc_entry_label.setStyleSheet("background-color: darkGray")

        self.voltageinc_input = QLineEdit()
        self.voltageinc_input.setText(str(default_vstep))

        # define Voltage Increment Box
        self.steptime_entry_label = QLabel()
        self.steptime_entry_label.setText('Set Voltage Step Time [s]')
        self.steptime_entry_label.setStyleSheet("background-color: darkGray")

        self.steptime_input = QLineEdit()
        self.steptime_input.setText(str(default_steptime))

        # define Time Box
        self.time_entry_label = QLabel()
        self.time_entry_label.setText('Set Duration [minutes]')
        self.time_entry_label.setStyleSheet("background-color: darkGray")

        self.time_input = QLineEdit()
        self.time_input.setText(str(default_duration))

        # define buttons
        self.start_button = QPushButton("Run")
        self.start_button.setCheckable(True)
        self.start_button.clicked.connect(self.start_button_clicked)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setCheckable(True)
        self.stop_button.clicked.connect(self.stop_button_clicked)
        self.stop_button.setDisabled(True)

        self.IO_button = QPushButton("Hardware I/O")
        self.IO_button.setCheckable(True)
        self.IO_button.clicked.connect(self.IO_button_clicked)

        # create spacers to make the layout pretty
        self.spacer1 = QLabel()
        self.spacer2 = QLabel()
        self.spacer3 = QLabel()
        self.spacer4 = QLabel()

        # Set Window Layout
        layout = QGridLayout()
        parentlayout = QGridLayout()

        layout.addWidget(self.file_entry_label, 0, 0)
        layout.addWidget(self.voltage_entry_label, 2, 0)
        layout.addWidget(self.voltageinc_entry_label, 4, 0)
        layout.addWidget(self.steptime_entry_label, 6, 0)
        layout.addWidget(self.time_entry_label, 8, 0)

        layout.addWidget(self.file_input, 0, 1)

        layout.addWidget(self.spacer1, 1, 1)
        layout.addWidget(self.voltage_input, 2, 1)

        layout.addWidget(self.spacer2, 3, 1)
        layout.addWidget(self.voltageinc_input, 4, 1)

        layout.addWidget(self.spacer3, 5, 1)
        layout.addWidget(self.steptime_input, 6, 1)

        layout.addWidget(self.spacer4, 7, 1)
        layout.addWidget(self.time_input, 8, 1)

        layout.addWidget(self.start_button, 4, 3)
        layout.addWidget(self.stop_button, 5, 3)
        layout.addWidget(self.IO_button, 0, 3)

        parentlayout.addLayout(layout, 0, 0)
        parentlayout.addWidget(self.graphWidget, 0, 1)

        container = QWidget()
        container.setLayout(parentlayout)
        self.setCentralWidget(container)

    def start_button_clicked(self):
        # change UI
        self.start_button.setText("Running")
        self.start_button.setEnabled(False)

        self.IO_button.setEnabled(False)

        self.stop_button.setEnabled(True)
        self.stop_button.setStyleSheet("background-color: red")

        self.file_input.setDisabled(True)
        self.voltage_input.setDisabled(True)
        self.voltageinc_input.setDisabled(True)
        self.steptime_input.setDisabled(True)
        self.time_input.setDisabled(True)

        # set variables for run

        self.voltage = float(self.voltage_input.text())
        self.vstep = float(self.voltageinc_input.text())
        self.steptime = float(self.steptime_input.text())
        self.duration = float(self.time_input.text())
        self.filename = self.file_input.text()
        print(self.voltage)
        print(self.vstep)
        print(self.steptime)
        print(self.duration)
        print(self.filename)


        self.startArduino()
        #sleep(30)
        #self.stop_button_clicked()
        result = self.startKeithley(self, self.filename, self.voltage, self.vstep, self.steptime, self.duration)
        #if result :
            #self.extractArduino()

        #self.stop_button_clicked()

    def stop_button_clicked(self):
        self.start_button.setText("Run")
        self.start_button.setEnabled(True)

        self.IO_button.setEnabled(True)

        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: lightGray")

        self.file_input.setDisabled(False)
        self.voltage_input.setDisabled(False)
        self.voltageinc_input.setDisabled(False)
        self.steptime_input.setDisabled(False)
        self.time_input.setDisabled(False)

        self.stopArduino()
        self.stopKeithley()
        self.timer.timeout.disconnect()

    def IO_button_clicked(self):
        dlg = CustomDialog(self)
        response = dlg.exec()
        if response:
            self.GPIB_address = dlg.returnGPIB()
            self.pumpchannel = dlg.returnPump()
            self.airchannel = dlg.returnAir()
            self.valvechannel = dlg.returnValve()

    def startArduino(self):
        ser.write(b'R')
        return True

    def extractArduino(self):
        ser.write(b'E')
        sleep(self.extractiontime)
        ser.write(b'S')
        return True

    def stopArduino(self):
        ser.write(b'L')
        return True

    def startKeithley(self,filename = 'filename', GPIB_address=4, set_voltage=50.0, voltage_increment=2.0, timestep=1.0,
                         duration=3.0):
        max_current = 0.1  # 100 miliamps
        duration_seconds = int(60*duration)
        address = "GPIB::" + str(GPIB_address)
        self.timer.timeout.connect(self.update_plot_data)
        #sleep(duration_seconds)
        #sourcemeter = Keithley2400(address)
        #sourcemeter.reset()
        #sourcemeter.use_front_terminals()
        #sourcemeter.measure_current()
        #sourcemeter.apply_voltage((set_voltage + 1), max_current)



        #sourcemeter.ramp_to_voltage(set_voltage, int(set_voltage/voltage_increment), timestep)




          # Update the data.
        #for i in range(duration_seconds+1):
            #currents[i] = sourcemeter.current
            #np.append(self.currents, i)
            #np.append(self.times, i)
            #self.data_line.setData(self.times, self.currents)
            #sleep(1)

        # Save the data columns in a CSV file
        #data = pd.DataFrame({
            #'Times (s)': self.times,
            #'Current (A)': self.currents,

        #})
        #data.to_csv(str(filename) + '.csv')

        return True

    def update_plot_data(self):
        self.times.append(self.times[-1] + 1)  # Add a new value 1 higher than the last.

        # self.y = self.y[1:]  # Remove the first
        self.currents.append(randint(0, 100))

        self.data_line.setData(self.times, self.currents)

    def stopKeithley(self):
        return True




# define the hardware IO window
class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Hardware I/O")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        GPIB_label = QLabel("GPIB Address")
        self.GPIB_input = QLineEdit()
        self.GPIB_input.setText(str(default_GPIB))

        pump_label = QLabel("Pump Channel")
        self.pump_input = QLineEdit()
        self.pump_input.setText(str(default_pumpchannel))

        air_label = QLabel("Air Channel")
        self.air_input = QLineEdit()
        self.air_input.setText(str(default_airchannel))

        valve_label = QLabel("Valve Channel")
        self.valve_input = QLineEdit()
        self.valve_input.setText(str(default_valvechannel))

        self.layout = QGridLayout()

        self.layout.addWidget(GPIB_label, 0, 0)
        self.layout.addWidget(self.GPIB_input, 0, 1)
        self.layout.addWidget(pump_label, 1, 0)
        self.layout.addWidget(self.pump_input, 1, 1)
        self.layout.addWidget(air_label, 2, 0)
        self.layout.addWidget(self.air_input, 2, 1)
        self.layout.addWidget(valve_label, 3, 0)
        self.layout.addWidget(self.valve_input, 3, 1)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def returnGPIB(self):
        return int(self.GPIB_input.text())

    def returnAir(self):
        return int(self.air_input.text())

    def returnPump(self):
        return int(self.pump_input.text())

    def returnValve(self):
        return int(self.valve_input.text())


app = QApplication(sys.argv)
app.setStyle('Breeze')
window = MainWindow()
window.show()

sys.exit(app.exec())
