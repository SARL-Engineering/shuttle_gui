from PyQt5 import QtCore, QtWidgets
import serial
from Framework.BoxHandlerCore import BoxHandler


class Settings(QtCore.QThread):
    def __init__(self, main_window):

        self.main_window = main_window
        self.settings_tab_layout = QtWidgets.QFormLayout()
        self.num_of_trials_box = QtWidgets.QSpinBox()
        self.settle_time_box = QtWidgets.QSpinBox()
        self.trial_dur_box = QtWidgets.QSpinBox()
        self.seek_time_box = QtWidgets.QSpinBox()
        self.it_settle_time_box = QtWidgets.QSpinBox()
        self.fault_out_swaps_box = QtWidgets.QSpinBox()
        self.fault_out_per_box = QtWidgets.QSpinBox()
        self.shock_voltage_box = QtWidgets.QDoubleSpinBox()
        self.shock_interval_box = QtWidgets.QSpinBox()
        self.shock_dur_box = QtWidgets.QSpinBox()
        self.num_of_trials_box.setRange(0, 255)
        self.settle_time_box.setRange(0, 255)
        self.trial_dur_box.setRange(0, 255)
        self.seek_time_box.setRange(0, 255)
        self.it_settle_time_box.setRange(0, 255)
        self.fault_out_swaps_box.setRange(0, 255)
        self.fault_out_per_box.setRange(0, 255)
        self.shock_voltage_box.setRange(0, 50.0)
        self.shock_interval_box.setRange(0, 10000)
        self.shock_dur_box.setRange(0, 3000)
        self.start()

    def setup_gui_settings(self):

        self.settings_tab_layout.addRow(QtWidgets.QLabel("Number of Trials"), self.num_of_trials_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Settle Time(m)"), self.settle_time_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Trial Duration(s)"), self.trial_dur_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Seek Time(s)"), self.seek_time_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Inter Trial Settle Time(s)"), self.it_settle_time_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Fault Out Swaps"), self.fault_out_swaps_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Fault Out %"), self.fault_out_per_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Shock Voltage(V)"), self.shock_voltage_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Shock Interval(ms)"), self.shock_interval_box)
        self.settings_tab_layout.addRow(QtWidgets.QLabel("Shock Duration(ms)"), self.shock_dur_box)

        return self.settings_tab_layout

