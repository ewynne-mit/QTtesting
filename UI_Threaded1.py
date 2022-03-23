# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 21:30:42 2022

@author: hanla
"""
import sys
import default_vals as df
import keithley_worker



import pandas as pd
from time import sleep
from datetime import datetime


import pyqtgraph as pg
#import pyqtgraph.exporters
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QDialog, \
    QDialogButtonBox

class MainWindow(QtWidgets.QMainWindow):
    
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.label = QLabel("0")
        
        self.GPIB_address = df.default_GPIB
        self.pumpchannel = df.default_pumpchannel
        self.airchannel = df.default_airchannel
        self.valvechannel = df.default_valvechannel
        self.filename = df.default_filename
        
        self.times = list(range(1))
        self.currents = list(range(1))
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setTitle("Current (A)", color="b", size="20pt")
        self.graphWidget.setLabel('left', 'Current (A)')
        self.graphWidget.setLabel('bottom', 'Time (~s)')
        
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 7)
        self.data_line = self.graphWidget.plot(self.times, self.currents, pen=pen)
        
        
        self.kworker = keithley_worker.KeithleyWorker()
        self.thread = QThread()
        
        self.kworker.intReady.connect(self.onIntReady)
        
        self.kworker.finished.connect(self.onFinish)
        
        self.kworker.moveToThread(self.thread)
        
        self.kworker.finished.connect(self.thread.quit)
        
        self.thread.started.connect(self.kworker.procCounter)
        
        
        
        
        self.create_ui()
        
        
    def onIntReady(self, i):
        
        self.times.append(self.times[-1] + 1)  # Add a new value 1 higher than the last.
        self.currents.append(i)
        self.data_line.setData(self.times, self.currents)
        
    def onFinish(self):
        data = pd.DataFrame({
            'Times (s)': self.times,
            'Current (A)': self.currents,

        })
        now = datetime.now()
        data.to_csv(str(self.filename)+'_' + now.strftime("%Y%m%d-%H%M%S") + '.csv')
    
    def create_ui(self):
        self.setWindowTitle("HT-Concentrator UI")
        
        
        # define File naming Box
        self.file_entry_label = QLabel()
        self.file_entry_label.setText('Enter Filename')
        self.file_entry_label.setStyleSheet("background-color: darkGray")

        self.file_input = QLineEdit()
        self.file_input.setText(df.default_filename)

        # define Voltage Box
        self.voltage_entry_label = QLabel()
        self.voltage_entry_label.setText('Set Voltage [V]')
        self.voltage_entry_label.setStyleSheet("background-color: darkGray")

        self.voltage_input = QLineEdit()
        self.voltage_input.setText(str(df.default_voltage))

        # define Voltage Increment Box
        self.voltageinc_entry_label = QLabel()
        self.voltageinc_entry_label.setText('Set Voltage Increment [V]')
        self.voltageinc_entry_label.setStyleSheet("background-color: darkGray")

        self.voltageinc_input = QLineEdit()
        self.voltageinc_input.setText(str(df.default_vstep))

        # define Voltage Increment Box
        self.steptime_entry_label = QLabel()
        self.steptime_entry_label.setText('Set Voltage Step Time [s]')
        self.steptime_entry_label.setStyleSheet("background-color: darkGray")

        self.steptime_input = QLineEdit()
        self.steptime_input.setText(str(df.default_steptime))

        # define Time Box
        self.time_entry_label = QLabel()
        self.time_entry_label.setText('Set Duration [minutes]')
        self.time_entry_label.setStyleSheet("background-color: darkGray")

        self.time_input = QLineEdit()
        self.time_input.setText(str(df.default_duration))

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
        voltage = float(self.voltage_input.text())
        vstep = float(self.voltageinc_input.text())
        steptime = float(self.steptime_input.text())
        duration = float(self.time_input.text())
        self.filename = self.file_input.text()
        
        self.kworker.setKeithley(self.GPIB_address,voltage,vstep,steptime,duration)
        sleep(4)
        self.thread.start()
        return True
    
    def stop_button_clicked(self):
        return True
    
    def IO_button_clicked(self):
        dlg = CustomDialog(self)
        response = dlg.exec()
        if response:
            self.GPIB_address = dlg.returnGPIB()
            self.pumpchannel = dlg.returnPump()
            self.airchannel = dlg.returnAir()
            self.valvechannel = dlg.returnValve()
            self.kworker.setArduino(self.airchannel,self.pumpchannel,self.valvechannel)
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
        self.GPIB_input.setText(str(df.default_GPIB))

        pump_label = QLabel("Pump Channel")
        self.pump_input = QLineEdit()
        self.pump_input.setText(str(df.default_pumpchannel))

        air_label = QLabel("Air Channel")
        self.air_input = QLineEdit()
        self.air_input.setText(str(df.default_airchannel))

        valve_label = QLabel("Valve Channel")
        self.valve_input = QLineEdit()
        self.valve_input.setText(str(df.default_valvechannel))

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



    
app = QtWidgets.QApplication(sys.argv)
test = MainWindow()
test.show()
app.exec()
