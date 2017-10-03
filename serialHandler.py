# Authors: Aaron Rito, Corwin Perren
# Date: 10/2/17
# Project: SARL Shuttlebox Behavior System
# Client: Oregon State University, SARL lab

########################################################################################################################
#   This thread is instantiated in the BoxHandlerCore file on line 52. Each instance of this thread will communicate   #
#   with it's own Shuttlebox, on it's own COM port. To access different threads, call functions in the BoxHandler class#
#   and send signals out to the other thread, including other instances of this one. It is safe to instantiate the     #
#   settings class and Qsettings handle, however, one should not instantiate the results class in this thread or risk  #
#   data corruption.                                                                                                   #
########################################################################################################################
from PyQt5 import QtCore, QtWidgets, QtGui
import serial
from Framework.BoxHandlerCore import BoxHandler
from mainFile import NewWindow
from settings_core import ShuttleSettings


class SerialThread(QtCore.QThread):

    updating_settings_signal = QtCore.pyqtSignal()
    updating_settings_signal_close = QtCore.pyqtSignal()

    def __init__(self, main_window, box_handler, comport_string):
        super(SerialThread, self).__init__()

        # inheritances
        self.main_window = main_window
        self.box_handler = box_handler
        self.comport_string = comport_string
        self.main_ref = NewWindow

        # Gui Object References
        self.id_list_widget = self.main_window.id_list_widget  # type: QtWidgets.QListWidget

        # Serial buffer and connection set up
        self.in_buffer = ""
        self.arduino = serial.Serial(comport_string, 57600, bytesize=8, stopbits=1, timeout=None)

        # Class variables
        self.should_run = True
        self.current_state = 0
        self.results_flag = 0
        self.current_state_label = "Wait for Start"
        self.current_state_strings = ["Wait for Start", "Test Start", "Settle Period", "Inter Trial", "Trial Start",
                                      "Trial Seek", "Trial Shock", "Trial End", "Abort", "Test End"]
        self.pattern_list = ["Heart", "Big X", "Big O", "Horizontal Lines", "Vertical Lines", "Diagonal Lines",
                             "Big Line", "Small Box", "Corners"]
        self.results = None
        self.update_flag = None
        self.settings_flag = False
        self.box_id_found_flag = False
        self.box_id = None

        # More static GUI elements
        self.box_tab_widget = None  # type: QtWidgets.QTabWidget
        self.tab_widget_w = self.main_window.tab_widget_widget

        self.__connect_signals_to_slots()

        # launching class instances last (for box_id)
        self.settings = QtCore.QSettings()
        self.settings_core = ShuttleSettings(main_window)
        self.counter = 0 #remove this before launch
        self.start()

    def __connect_signals_to_slots(self):
        self.main_window.id_list_widget.currentRowChanged.connect(self.on_current_box_id_changed_slot)
        self.main_window.stop_all_threads.connect(self.on_stop_all_threads_slot)
        self.box_handler.start_all_boxes_signal.connect(self.on_start_all_boxes)
        self.box_handler.abort_all_boxes_signal.connect(self.on_abort_all_boxes)
        self.updating_settings_signal.connect(self.show_update_wait)

    def run(self):
        while self.should_run:
                if self.arduino.inWaiting():
                    in_byte = self.arduino.read().decode("utf-8")
                    self.in_buffer += in_byte
                    if in_byte == "\n":
                        if "show: " in self.in_buffer:
                            # report box ready to BoxHandler
                            self.box_handler.box_counter()

                        if "u: " in self.in_buffer:
                            # The updates to a Shuttlebox are complete
                            self.update_flag = True
                            self.box_handler.send_data_init(self.box_id)
                            self.updating_settings_signal_close.emit()

                        if "Box ID: " in self.in_buffer:
                            # The system found an active Shuttlebox
                            self.box_id_found_flag = True
                            self.box_id = int(self.in_buffer.split(": ")[1])
                            print("Box ID: " + str(self.box_id) + " found")

                        if "s: " in self.in_buffer:
                            # The current state of the Shuttlebox has changed
                            self.current_state = int(self.in_buffer.split(": ")[1])
                            print("STATE = " + str(self.current_state))
                            if self.box_tab_widget:
                                self.update_status_label(int(self.current_state))

                        if "z, " in self.in_buffer:
                            # The assay has ended or the trial has been aborted, results received from Arduino.
                            self.results = self.in_buffer.split(", ")
                            self.results.pop()
                            self.results.pop(0)
                            self.results.pop(0)
                            self.results.pop(0)
                            print("popped results", self.results)
                            self.box_handler.send_data(self.results, self.box_id)
                            self.results_flag = 1

                        if "x: " in self.in_buffer:
                            # The Shuttlebox is requesting it's settings
                            print("sending configs to box " + str(self.box_id))
                            self.send_to_box(self.settings_core.send_box_configs(self.box_id))
                            self.send_to_box(self.settings_core.send_settle_lights(self.box_id))
                            self.send_to_box(self.settings_core.send_trial_lights(self.box_id))
                            self.send_to_box(self.settings_core.send_start_lights(self.box_id))

                            ################ If there is a problem updating boxes, use these to verify the arduino######
                            # self.send_to_box(" ")
                            # self.send_to_box("50,1,600,24,12,12,16,8,95,20,500,50,5")
                            # self.send_to_box("4,8,100,150,255,0,255,0,50,75,255,0,255,0,200,225,255,0,255,200,0,1")
                            # self.send_to_box("7,3,200,15,12,255,10,255,50,75,0,255,0,255,200,225,0,255,255,200,1,0")
                            # self.send_to_box("7,3,200,15,12,255,10,255,50,75,0,255,0,255,200,225,0,255,255,200,1,0")

                        print(self.in_buffer)
                        self.in_buffer = ""
                self.msleep(50)
                self.arduino.flush()

########################################################################################################################
#   These functions support the settings updates, and handle updating the GUI when the list item is changed.           #
########################################################################################################################

    def send_to_box(self, message):
        self.arduino.write(bytes(str(message), "utf-8"))

    # !!!!VERY IMPORTANT!!!! This function updates the settings in the registry, the widgets, and the arduinos.
    # It is called whenever there is a default reset or a box update. Called from multiple button....
    def update_settings_slot(self):
        # Make sure the box isn't running before updating
        if self.current_state != 0:
            m = QtWidgets.QMessageBox()
            m.setInformativeText("Error: Cannot update Shuttlebox while trial is running.")
            m.exec()
        else:
            self.box_tab_widget.hide()
            m = QtWidgets.QMessageBox()
            m.setInformativeText("Are you sure you want to update Shuttlebox " + str(self.box_id))
            m.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            m.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            m.setModal(True)
            x = m.exec()

            if x == QtWidgets.QMessageBox.Ok:
                self.counter = 0 ##############remove this before launch#################################
                # Setup the waiting progress window
                self.welcome = QtWidgets.QProgressDialog()
                self.welcome.setCancelButton(None)
                self.welcome.setRange(0, 0)
                self.my_font = QtGui.QFont()
                self.my_font.setPointSizeF(11)
                self.my_font.setBold(True)
                self.welcome.setFont(self.my_font)
                self.welcome.setWindowTitle("SARL Shuttlebox Behavior System")
                self.welcome_label = QtWidgets.QLabel(
                    "       Please wait while Shuttlebox " + str(self.box_id) +
                    " is updated.\n                  This may take a moment....")
                self.welcome_button = QtWidgets.QPushButton(None)
                self.welcome_window = QtWidgets.QGraphicsScene()
                self.welcome_image = QtGui.QImage("logo.png")
                self.lab = QtWidgets.QLabel()
                self.imageLabel = QtWidgets.QLabel()
                self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.welcome_image))
                layout = QtWidgets.QVBoxLayout()
                layout.addWidget(self.imageLabel)
                layout.addWidget(self.welcome_label)
                layout.addSpacing(50)
                self.welcome.setLayout(layout)
                self.welcome.resize(250, 200)
                self.welcome.setModal(True)
                self.welcome.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                self.updating_settings_signal_close.connect(self.close_update)

                # Send the signals to update the box
                self.update_flag = False
                self.settings_core.update_settings(self.box_id)
                self.box_handler.send_data_init(self.box_id)
                self.send_to_box(self.box_id)
                self.send_to_box(",")
                self.send_to_box("249")

                # Show the progress bar, it's closed by a signal from the serial input on line ..
                self.updating_settings_signal.emit()
                msg_box = QtWidgets.QMessageBox()
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg_box.setText("Settings Updated")
                msg_box.exec()
                self.box_tab_widget.show()
                self.update_flag = False
                self.settings_flag = False
            self.box_tab_widget.show()

    # These two functions handle the progress window
    def show_update_wait(self):
        self.welcome.exec_()

    def close_update(self):
        self.welcome.done(0)

    # VERY IMPORTANT this function builds the new tabs when a box id is changed from the list. It also destroys the
    # GUI elements from the tab being clicked away from. The thread for the Shuttlebox will still be active and
    # rec/send data over serial. It's important to rememeber the GUI elements do not exist outside of the clicked tab.
    # when the settings change they will be updated in registry and retrieved when the new id is clicked on.

    def on_current_box_id_changed_slot(self, row_id):
        list_box_id = int(self.id_list_widget.currentItem().text())
        # list_box_id = row_id + 1
        if list_box_id == self.box_id:
            layout = self.tab_widget_w.layout()  # type: QtWidgets.QLayout

            for i in reversed(range(layout.count())):
                widgetToRemove = layout.itemAt(i).widget()
                # remove it from the layout list
                layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

            # Make a new tab widget(yes all of it) and set it to the main layout, update settings
            layout.addWidget(self.make_box_tab_widget(self.tab_widget_w))
            self.id_list_widget.sortItems()
            self.update_status_label(int(self.current_state))
            self.box_handler.send_data_init(int(row_id + 1))

########################################################################################################################
########################################################################################################################
#                                                                                                                      #
#   Make the GUI tabs and retrieve the settings for the selected box (runs 600+ lines)                                 #
#                                                                                                                      #
########################################################################################################################
########################################################################################################################

########################################################################################################################
#   Build the box tab. This function runs most of the code on this thread to build a new box tab with populated windows#
########################################################################################################################

    def make_box_tab_widget(self, parent):
        self.box_tab_widget = QtWidgets.QTabWidget(parent)
        self.make_control_tab(parent)
        self.make_settings_tab(parent)
        self.make_lights_tab(parent)
        self.make_admin_tab(parent)
        return self.box_tab_widget

########################################################################################################################
#   Build the Admin Tab                                                                                                #
########################################################################################################################

    def make_admin_tab(self, parent):
        admin_tab_widget = QtWidgets.QWidget(parent)
        self.box_tab_widget.addTab(admin_tab_widget, "Admin")
        admin_layout = QtWidgets.QFormLayout()
        self.restore_all_def_button = QtWidgets.QPushButton("THINK FIRST")
        self.restore_all_def_button.clicked.connect(self.restore_all_def_slot)
        self.restore_def_button = QtWidgets.QPushButton("MOSTLY SAFE")
        self.restore_def_button.clicked.connect(self.restore_def_slot)
        self.apply_all_button = QtWidgets.QPushButton("APPLY TO ALL")
        self.apply_all_button.clicked.connect(self.apply_all_slot)
        self.options_button = QtWidgets.QPushButton("OPTIONS")
        self.options_button.clicked.connect(self.options_slot)

        # add buttons to the layout
        admin_layout.addRow("Restore defaults for Shuttlebox " + str(self.box_id), self.restore_def_button)
        admin_layout.addRow("Restore all defaults", self.restore_all_def_button)
        admin_layout.addRow("Apply settings to all boxes", self.apply_all_button)
        admin_layout.addRow("Preferences", self.options_button)
        admin_layout.setHorizontalSpacing(10)
        holder_layout = QtWidgets.QHBoxLayout()
        holder_layout.addSpacing(220)
        holder_layout.addLayout(admin_layout)
        admin_tab_widget.setLayout(holder_layout)

    # Admin slots
    def options_slot(self):
        self.box_handler.font_signal()

    def apply_all_slot(self):
        msg = QtWidgets.QMessageBox()
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        msg.setInformativeText("Are you sure you want to apply the settings from Shuttlebox " + str(self.box_id) +
                               " to all Shuttlebox settings?")
        x = msg.exec()
        if x == QtWidgets.QMessageBox.Ok:
            self.settings_core.apply_all_settings(self.box_id)
            msg = QtWidgets.QMessageBox()
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msg.setInformativeText("Settings from Shuttlebox " + str(self.box_id) +
                                   " applied to all Shuttlebox settings. " +
                                   "Please restart the program to update the boxes")
            msg.exec()

    def restore_all_def_slot(self):
        if self.current_state != 0:
            m = QtWidgets.QMessageBox()
            m.setInformativeText("Error: Cannot update Shuttlebox while trial is running.")
            m.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            m.exec()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Are you absolutely sure you want to restore the defaults for ALL Shuttleboxes?")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.RestoreDefaults | QtWidgets.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            msgBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.RestoreDefaults:
                self.settings_core.restore_all_defaults()
                self.get_conf_settings()
                self.control_id_box.setText(self.settings.value(("control_number/box_id_" + str(self.box_id))))
                self.concentrate_box.setText(self.settings.value("concentrate/box_id_", str(self.box_id)))
                self.get_settle_lights_settings()
                self.get_trial_lights_settings()
                self.get_start_lights_settings()
                msgBox = QtWidgets.QMessageBox()
                msgBox.setText("Defaults restored. Please restart the program to update the Shuttleboxes.")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
                msgBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                msgBox.exec_()

    def restore_def_slot(self):
        if self.current_state != 0:
            m = QtWidgets.QMessageBox()
            m.setInformativeText("Error: Cannot update Shuttlebox while trial is running.")
            m.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            m.exec()
        else:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setText("Are you absolutely sure you want to restore the defaults for Shuttlebox " + str(self.box_id) +
                           "?")
            msgbox.setStandardButtons(QtWidgets.QMessageBox.RestoreDefaults | QtWidgets.QMessageBox.Cancel)
            msgbox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msgbox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            ret = msgbox.exec_()
            if ret == QtWidgets.QMessageBox.RestoreDefaults:
                self.settings_core.restore_box_defaults(self.box_id)
                self.update_settings_slot()
                self.get_conf_settings()
                self.control_id_box.setText(self.settings.value(("control_number/box_id_" + str(self.box_id))))
                self.concentrate_box.setText(self.settings.value("concentrate/box_id_" + str(self.box_id)))
                self.get_settle_lights_settings()
                self.get_trial_lights_settings()
                self.get_start_lights_settings()

########################################################################################################################
#   Build the settings tab                                                                                             #
########################################################################################################################

    def make_settings_tab(self, parent):
        self.settings_tab_widget = QtWidgets.QWidget(parent)
        self.box_tab_widget.addTab(self.settings_tab_widget, "Settings")
        settings_layout = QtWidgets.QFormLayout()
        settings_layout2 = QtWidgets.QFormLayout()

        # make the boxes
        self.n_of_trials_box = QtWidgets.QSpinBox()
        self.selection_box = QtWidgets.QSpinBox()
        self.settle_time_box = QtWidgets.QSpinBox()
        self.trial_duration_box = QtWidgets.QSpinBox()
        self.seek_time_box = QtWidgets.QSpinBox()
        self.trial_settle_box = QtWidgets.QSpinBox()
        self.fault_side_box = QtWidgets.QSpinBox()
        self.fault_out_box = QtWidgets.QSpinBox()
        self.shock_voltage_box = QtWidgets.QSpinBox()
        self.shock_interval_box = QtWidgets.QSpinBox()
        self.shock_duration_box = QtWidgets.QSpinBox()
        self.success_trials_box = QtWidgets.QSpinBox()
        self.update_button = QtWidgets.QPushButton("UPDATE BOX " + str(self.box_id))

        # add the elements to the layout
        settings_layout.addRow("Number of Trials", self.n_of_trials_box)
        settings_layout.addRow("Selection Mode", self.selection_box)
        settings_layout.addRow("Settle Time (m)", self.settle_time_box)
        settings_layout.addRow("Trial Duration (s)", self.trial_duration_box)
        settings_layout.addRow("Seek Time (s)", self.seek_time_box)
        settings_layout.addRow("Trial Settle Time (s)", self.trial_settle_box)
        settings_layout.addRow("Fault Out Sideswaps", self.fault_side_box)
        settings_layout.addRow("Fault Out Percent (%)", self.fault_out_box)
        settings_layout.addRow("Shock Voltage (V)", self.shock_voltage_box)
        settings_layout.addRow("Shock Interval (ms)", self.shock_interval_box)
        settings_layout.addRow("Shock Duration (ms)", self.shock_duration_box)
        settings_layout.addRow("Successful Trials", self.success_trials_box)
        settings_layout2.addRow("Save Settings", self.update_button)

        # set the ranges
        self.n_of_trials_box.setRange(0, 255)
        self.selection_box.setRange(0, 1)
        self.settle_time_box.setRange(0, 1000)
        self.trial_duration_box.setRange(0, 255)
        self.seek_time_box.setRange(0, 255)
        self.trial_settle_box.setRange(0, 255)
        self.fault_side_box.setRange(0, 255)
        self.fault_out_box.setRange(0, 100)
        self.shock_voltage_box.setRange(0, 24)
        self.shock_interval_box.setRange(0, 1000)
        self.shock_duration_box.setRange(0, 1000)
        self.success_trials_box.setRange(0, 255)

        # Get the settings
        self.get_conf_settings()

        # connect the slots
        self.n_of_trials_box.valueChanged.connect(self.n_of_trials_slot)
        self.selection_box.valueChanged.connect(self.selection_slot)
        self.settle_time_box.valueChanged.connect(self.settle_time_slot)
        self.trial_duration_box.valueChanged.connect(self.trial_duration_slot)
        self.seek_time_box.valueChanged.connect(self.seek_time_slot)
        self.trial_settle_box.valueChanged.connect(self.trial_settle_slot)
        self.fault_side_box.valueChanged.connect(self.fault_side_slot)
        self.fault_out_box.valueChanged.connect(self.fault_out_slot)
        self.shock_voltage_box.valueChanged.connect(self.shock_voltage_slot)
        self.shock_voltage_box.valueChanged.connect(self.shock_voltage_slot)
        self.shock_interval_box.valueChanged.connect(self.shock_interval_slot)
        self.shock_duration_box.valueChanged.connect(self.shock_duration_slot)
        self.success_trials_box.valueChanged.connect(self.success_trials_slot)
        self.update_button.clicked.connect(self.update_settings_slot)

        # Apply the layouts
        holder_layout = QtWidgets.QVBoxLayout()
        top_layout = QtWidgets.QHBoxLayout()
        bottom_layout = QtWidgets.QHBoxLayout()
        top_layout.addSpacing(10)
        top_layout.addLayout(settings_layout)
        bottom_layout.addSpacing(260)
        bottom_layout.addLayout(settings_layout2)
        settings_layout.setHorizontalSpacing(100)
        settings_layout.setVerticalSpacing(10)
        settings_layout2.setHorizontalSpacing(100)
        holder_layout.addLayout(top_layout)
        holder_layout.addSpacing(200)
        holder_layout.addLayout(bottom_layout)
        self.settings_tab_widget.setLayout(holder_layout)

    # Settings Slots
    def get_conf_settings(self):
        # retrieve the settings
        self.n_of_trials_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/n_of_trials"), int))
        self.selection_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "selection_mode"), int))
        self.settle_time_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/settle_time"), int))
        self.trial_duration_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/trial_duration"),
                                int))
        self.seek_time_box.setValue(self.settings.value(("boxes/box_id_" + str(self.box_id) + "/seek_time"), int))
        self.trial_settle_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/trial_settle_time"),
                                int))
        self.fault_side_box.setValue(self.settings.value(("boxes/box_id_" + str(self.box_id) + "/fault_out_side"),
                                                         int))
        self.fault_out_box.setValue(self.settings.value(("boxes/box_id_" + str(self.box_id) + "/fault_out_percent"),
                                                        int))
        self.shock_voltage_box.setValue(self.settings.value(("boxes/box_id_" + str(self.box_id) + "/shock_voltage"),
                                                            int))
        self.shock_interval_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/shock_interval"),
                                int))
        self.shock_duration_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/shock_duration"),
                                int))
        self.success_trials_box.setValue(
            self.settings.value(("boxes/box_id_" + str(self.box_id) + "/success_trials"),
                                int))

#################### WRITE A FUNCTION HERE TO DEAL WITH THESE#####################################################

    def n_of_trials_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/n_of_trials"), self.n_of_trials_box.value())

    def selection_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "selection_mode"), self.selection_box.value())

    def settle_time_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/settle_time"), self.settle_time_box.value())

    def trial_duration_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/trial_duration"),
                               self.trial_duration_box.value())

    def seek_time_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/seek_time"), self.seek_time_box.value())

    def trial_settle_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/trial_settle_time"),
                               self.trial_settle_box.value())

    def fault_side_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/fault_out_side"),
                               self.fault_side_box.value())

    def fault_out_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/fault_out_percent"),
                               self.fault_out_box.value())

    def shock_voltage_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/shock_voltage"),
                               self.shock_voltage_box.value())

    def shock_interval_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/shock_interval"),
                               self.shock_interval_box.value())

    def shock_duration_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/shock_duration"),
                               self.shock_duration_box.value())

    def success_trials_slot(self):
        self.settings_flag = True
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/success_trials"),
                               self.success_trials_box.value())

########################################################################################################################
#   Build the lighting tab                                                                                             #
########################################################################################################################

    def make_lights_tab(self, parent):
        lights_tab_widget = QtWidgets.QWidget(parent)
        self.box_tab_widget.addTab(lights_tab_widget, "Lights")
        lights_tab_layout = QtWidgets.QFormLayout()

        # #################SETTLE LIGHTS################################################################################

        # make the buttons
        self.settle_lights_r_pattern_button = QtWidgets.QComboBox()
        self.settle_lights_r_pattern_button.insertItems(0, self.pattern_list)
        self.settle_lights_l_pattern_button = QtWidgets.QComboBox()
        self.settle_lights_l_pattern_button.insertItems(0, self.pattern_list)
        self.settle_lights_r_button = QtWidgets.QPushButton()
        self.settle_lights_l_button = QtWidgets.QPushButton()
        self.settle_lights_rb_button = QtWidgets.QPushButton()
        self.settle_lights_lb_button = QtWidgets.QPushButton()

        self.get_settle_lights_settings()

        # add the buttons to the layout
        lights_tab_layout.addRow("Right Side Settle Pattern", self.settle_lights_r_pattern_button)
        lights_tab_layout.addRow("Right Side Settle Lights Color", self.settle_lights_r_button)
        lights_tab_layout.addRow("Right Side Settle Lights Background Color", self.settle_lights_rb_button)
        lights_tab_layout.addRow("Left Side Settle Pattern", self.settle_lights_l_pattern_button)
        lights_tab_layout.addRow("Left Side Settle Lights Color", self.settle_lights_l_button)
        lights_tab_layout.addRow("Left Side Settle Lights Background Color", self.settle_lights_lb_button)

        # connect the slots
        self.settle_lights_r_button.clicked.connect(lambda: self.color_select_slot("settle_lights", "right_side_color",
                                                                                   "right_side_sat", "right_side_bright"
                                                                                   , self.settle_lights_r_button))
        self.settle_lights_rb_button.clicked.connect(lambda: self.color_select_slot("settle_lights", "right_back_color",
                                                                                    "right_back_sat",
                                                                                    "right_back_bright",
                                                                                    self.settle_lights_rb_button))
        self.settle_lights_l_button.clicked.connect(lambda: self.color_select_slot("settle_lights", "left_side_color",
                                                                                   "left_side_sat", "left_side_bright"
                                                                                   , self.settle_lights_l_button))
        self.settle_lights_lb_button.clicked.connect(lambda: self.color_select_slot("settle_lights", "left_back_color",
                                                                                    "left_back_sat", "left_back_bright"
                                                                                    , self.settle_lights_lb_button))
        self.settle_lights_r_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "settle_lights", "right_pattern", self.settle_lights_r_pattern_button.currentIndex()))
        self.settle_lights_l_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "settle_lights", "left_pattern", self.settle_lights_l_pattern_button.currentIndex()))

        # #######################TRIAL LIGHTS###########################################################################

        # make the buttons
        self.trial_lights_r_pattern_button = QtWidgets.QComboBox()
        self.trial_lights_r_pattern_button.insertItems(0, self.pattern_list)
        self.trial_lights_l_pattern_button = QtWidgets.QComboBox()
        self.trial_lights_l_pattern_button.insertItems(0, self.pattern_list)
        self.trial_lights_r_button = QtWidgets.QPushButton()
        self.trial_lights_l_button = QtWidgets.QPushButton()
        self.trial_lights_rb_button = QtWidgets.QPushButton()
        self.trial_lights_lb_button = QtWidgets.QPushButton()

        # get the settings
        self.get_trial_lights_settings()

        # add the buttons to the layout
        lights_tab_layout.addRow("Right Side trial Pattern", self.trial_lights_r_pattern_button)
        lights_tab_layout.addRow("Right Side trial Lights Color", self.trial_lights_r_button)
        lights_tab_layout.addRow("Right Side trial Lights Background Color", self.trial_lights_rb_button)
        lights_tab_layout.addRow("Left Side trial Pattern", self.trial_lights_l_pattern_button)
        lights_tab_layout.addRow("Left Side trial Lights Color", self.trial_lights_l_button)
        lights_tab_layout.addRow("Left Side trial Lights Background Color", self.trial_lights_lb_button)

        # connect the slots
        self.trial_lights_r_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "right_side_color",
                                                                                  "right_side_sat", "right_side_bright"
                                                                                  , self.trial_lights_r_button))
        self.trial_lights_rb_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "right_back_color",
                                                                                   "right_back_sat", "right_back_bright"
                                                                                   , self.trial_lights_rb_button))
        self.trial_lights_l_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "left_side_color",
                                                                                  "left_side_sat", "left_side_bright",
                                                                                  self.trial_lights_l_button))
        self.trial_lights_lb_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "left_back_color",
                                                                                   "left_back_sat", "left_back_bright",
                                                                                   self.trial_lights_lb_button))
        self.trial_lights_r_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "trial_lights", "right_pattern", self.trial_lights_r_pattern_button.currentIndex()))
        self.trial_lights_l_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "trial_lights", "left_pattern", self.trial_lights_l_pattern_button.currentIndex()))

        # #################START LIGHTS ################################################################################

        #make the buttons
        self.start_lights_r_pattern_button = QtWidgets.QComboBox()
        self.start_lights_r_pattern_button.insertItems(0, self.pattern_list)

        self.start_lights_l_pattern_button = QtWidgets.QComboBox()
        self.start_lights_l_pattern_button.insertItems(0, self.pattern_list)

        self.start_lights_r_button = QtWidgets.QPushButton()
        self.start_lights_l_button = QtWidgets.QPushButton()
        self.start_lights_rb_button = QtWidgets.QPushButton()
        self.start_lights_lb_button = QtWidgets.QPushButton()

        self.get_start_lights_settings()

        # add the buttons to the layout
        lights_tab_layout.addRow("Right Side start Pattern", self.start_lights_r_pattern_button)
        lights_tab_layout.addRow("Right Side start Lights Color", self.start_lights_r_button)
        lights_tab_layout.addRow("Right Side start Lights Background Color", self.start_lights_rb_button)
        lights_tab_layout.addRow("Left Side start Pattern", self.start_lights_l_pattern_button)
        lights_tab_layout.addRow("Left Side start Lights Color", self.start_lights_l_button)
        lights_tab_layout.addRow("Left Side start Lights Background Color", self.start_lights_lb_button)

        # connect the slots
        self.start_lights_r_button.clicked.connect(lambda: self.color_select_slot("start_lights", "right_side_color",
                                                                                  "right_side_sat", "right_side_bright"
                                                                                  , self.start_lights_r_button))
        self.start_lights_rb_button.clicked.connect(lambda: self.color_select_slot("start_lights", "right_back_color",
                                                                                   "right_back_sat",
                                                                                   "right_back_bright",
                                                                                   self.start_lights_rb_button))
        self.start_lights_l_button.clicked.connect(lambda: self.color_select_slot("start_lights", "left_side_color",
                                                                                  "left_side_sat", "left_side_bright"
                                                                                  , self.start_lights_l_button))
        self.start_lights_lb_button.clicked.connect(lambda: self.color_select_slot("start_lights", "left_back_color",
                                                                                   "left_back_sat", "left_back_bright"
                                                                                   , self.start_lights_lb_button))
        self.start_lights_r_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "start_lights", "right_pattern", self.start_lights_r_pattern_button.currentIndex()))
        self.start_lights_l_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "start_lights", "left_pattern", self.start_lights_l_pattern_button.currentIndex()))

        # Update button
        lights_tab_layout2 = QtWidgets.QFormLayout()
        self.light_update_button = QtWidgets.QPushButton("UPDATE BOX" + str(self.box_id))
        lights_tab_layout2.addRow("Save Settings", self.light_update_button)
        self.light_update_button.clicked.connect(self.update_settings_slot)

        # layouts
        holder_layout = QtWidgets.QVBoxLayout()
        holder_layout.addLayout(lights_tab_layout)
        holder_layout.addSpacing(10)
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addSpacing(260)
        bottom_layout.addLayout(lights_tab_layout2)
        holder_layout.addLayout(bottom_layout)
        holder_layout.addSpacing(10)
        lights_tab_layout.setHorizontalSpacing(50)
        lights_tab_layout.setVerticalSpacing(10)
        lights_tab_layout2.setHorizontalSpacing(100)
        lights_tab_layout2.setVerticalSpacing(10)
        lights_tab_widget.setLayout(holder_layout)

    # Lighting slots
    def get_settle_lights_settings(self):
        # patterns
        self.settle_lights_r_pattern_button.setCurrentIndex(self.settings.value("lights/settle_lights/box_id_" +
                                                                                str(self.box_id) + "right_pattern", int)
                                                            )
        self.settle_lights_l_pattern_button.setCurrentIndex(self.settings.value("lights/settle_lights/box_id_" +
                                                                                str(self.box_id) + "left_pattern", int))
        # make the custom colors from the saved settings
        self.settle_lights_r_color = QtGui.QColor()
        self.settle_lights_l_color = QtGui.QColor()
        self.settle_lights_rb_color = QtGui.QColor()
        self.settle_lights_lb_color = QtGui.QColor()

        # set the colors to the buttons
        self.settle_lights_r_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                              "right_side_color", int),
                                          self.settings.value(("lights/settle_lights/box_id_" + str(self.box_id) +
                                                               "right_side_sat"), int), self.settings.value((
                "lights/settle_lights/box_id_" + str(self.box_id) +
                "right_side_bright"), int))
        self.settle_lights_rb_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                               "right_back_color", int), self.settings.value(
            ("lights/settle_lights/box_id_" + str(self.box_id) + "right_back_sat"), int), self.settings.value(
            ("lights/settle_lights/box_id_" + str(self.box_id) + "right_back_bright"), int))
        self.settle_lights_l_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                              "left_side_color", int),
                                          self.settings.value(("lights/settle_lights/box_id_" + str(self.box_id) +
                                                               "left_side_sat"), int), self.settings.value(
                ("lights/settle_lights/box_id_" + str(self.box_id) + "left_side_bright"), int))
        self.settle_lights_lb_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                               "left_back_color", int), self.settings.value(
            ("lights/settle_lights/box_id_" + str(self.box_id) + "left_back_sat"), int), self.settings.value(
            ("lights/settle_lights/box_id_" + str(self.box_id) + "left_back_bright"), int))

        # style
        self.settle_lights_r_button.setStyleSheet("QWidget { background-color: %s}" % self.settle_lights_r_color.name())
        self.settle_lights_rb_button.setStyleSheet(
            "QWidget { background-color: %s}" % self.settle_lights_rb_color.name())
        self.settle_lights_l_button.setStyleSheet("QWidget { background-color: %s}" % self.settle_lights_l_color.name())
        self.settle_lights_lb_button.setStyleSheet(
            "QWidget { background-color: %s}" % self.settle_lights_lb_color.name())

    def get_trial_lights_settings(self):
        # make the custom colors from the saved settings
        self.trial_lights_r_color = QtGui.QColor()
        self.trial_lights_l_color = QtGui.QColor()
        self.trial_lights_rb_color = QtGui.QColor()
        self.trial_lights_lb_color = QtGui.QColor()

        #Patterns
        self.trial_lights_r_pattern_button.setCurrentIndex(self.settings.value("lights/trial_lights/box_id_" +
                                                                               str(self.box_id) + "right_pattern", int)
                                                           )
        self.trial_lights_l_pattern_button.setCurrentIndex(self.settings.value("lights/trial_lights/box_id_" +
                                                                               str(self.box_id) + "left_pattern", int))
        self.trial_lights_r_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                             "right_side_color", int),
                                         self.settings.value(("lights/trial_lights/box_id_" + str(self.box_id) +
                                                              "right_side_sat"), int), self.settings.value((
                "lights/trial_lights/box_id_" + str(self.box_id) +
                "right_side_bright"), int))
        self.trial_lights_rb_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                              "right_back_color", int), self.settings.value(
            ("lights/trial_lights/box_id_" + str(self.box_id) + "right_back_sat"), int), self.settings.value(
            ("lights/trial_lights/box_id_" + str(self.box_id) + "right_back_bright"), int))
        self.trial_lights_l_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                             "left_side_color", int),
                                         self.settings.value(("lights/trial_lights/box_id_" + str(self.box_id) +
                                                              "left_side_sat"), int), self.settings.value(
                ("lights/trial_lights/box_id_" + str(self.box_id) + "left_side_bright"), int))
        self.trial_lights_lb_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                              "left_back_color", int), self.settings.value(
            ("lights/trial_lights/box_id_" + str(self.box_id) + "left_back_sat"), int), self.settings.value(
            ("lights/trial_lights/box_id_" + str(self.box_id) + "left_back_bright"), int))

        # style
        self.trial_lights_r_button.setStyleSheet("QWidget { background-color: %s}" % self.trial_lights_r_color.name())
        self.trial_lights_rb_button.setStyleSheet("QWidget { background-color: %s}" % self.trial_lights_rb_color.name())
        self.trial_lights_l_button.setStyleSheet("QWidget { background-color: %s}" % self.trial_lights_l_color.name())
        self.trial_lights_lb_button.setStyleSheet("QWidget { background-color: %s}" % self.trial_lights_lb_color.name())

    def get_start_lights_settings(self):
        # make the custom colors from the saved settings
        self.start_lights_r_color = QtGui.QColor()
        self.start_lights_l_color = QtGui.QColor()
        self.start_lights_rb_color = QtGui.QColor()
        self.start_lights_lb_color = QtGui.QColor()
        self.start_lights_r_pattern_button.setCurrentIndex(self.settings.value("lights/start_lights/box_id_" +
                                                                               str(self.box_id) + "right_pattern", int))
        self.start_lights_l_pattern_button.setCurrentIndex(self.settings.value("lights/start_lights/box_id_" +
                                                                               str(self.box_id) + "left_pattern", int))
        self.start_lights_r_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                             "right_side_color", int),
                                         self.settings.value(("lights/start_lights/box_id_" + str(self.box_id) +
                                                              "right_side_sat"), int), self.settings.value((
                "lights/start_lights/box_id_" + str(self.box_id) +
                "right_side_bright"), int))
        self.start_lights_rb_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                              "right_back_color", int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "right_back_sat"), int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "right_back_bright"), int))
        self.start_lights_l_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                             "left_side_color", int),
                                         self.settings.value(("lights/start_lights/box_id_" + str(self.box_id) +
                                                              "left_side_sat"), int), self.settings.value(
                ("lights/start_lights/box_id_" + str(self.box_id) + "left_side_bright"), int))
        self.start_lights_lb_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                              "left_back_color", int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "left_back_sat"), int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "left_back_bright"), int))

        # style
        self.start_lights_r_button.setStyleSheet("QWidget { background-color: %s}" % self.start_lights_r_color.name())
        self.start_lights_rb_button.setStyleSheet("QWidget { background-color: %s}" % self.start_lights_rb_color.name())
        self.start_lights_l_button.setStyleSheet("QWidget { background-color: %s}" % self.start_lights_l_color.name())
        self.start_lights_lb_button.setStyleSheet("QWidget { background-color: %s}" % self.start_lights_lb_color.name())

    # This function selects the color and updates the GUI
    def color_select_slot(self, lights, hue, sat, val, button):
        self.settings_flag = True
        temp_colorbox = QtWidgets.QColorDialog()
        temp_color = temp_colorbox.getColor()
        button.setStyleSheet("QWidget { background-color: %s}" % temp_color.name())
        temp = temp_color.getHsv()
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + hue + ""), int(temp[0]))
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + sat + ""), int(temp[1]))
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + val + ""), int(temp[2]))

    # Select a pattern
    def pattern_select_slot(self, lights, pat, button):
        self.settings_flag = True
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + pat + ""),
                               button)

########################################################################################################################
#   Build the Control Tab                                                                                              #
########################################################################################################################

    def make_control_tab(self, parent):
        # Setting the layout
        control_tab_widget = QtWidgets.QWidget(parent)
        self.box_tab_widget.addTab(control_tab_widget, "Control " + str(self.box_id))
        control_form_layout = QtWidgets.QFormLayout()
        control_form_layout2 = QtWidgets.QFormLayout()
        control_box_layout = QtWidgets.QVBoxLayout()

        # Creating the button instances
        self.current_state_show = QtWidgets.QLabel()
        self.current_state_show.setText(str(self.current_state_label))
        self.control_id_box = QtWidgets.QTextEdit()
        self.concentrate_box = QtWidgets.QTextEdit()
        self.control_id_box.setText(self.settings.value(("control_number/box_id_" + str(self.box_id))))
        self.concentrate_box = QtWidgets.QTextEdit()
        self.concentrate_box.setText(self.settings.value("concentrate/box_id_" + str(self.box_id)))
        control_start_button = QtWidgets.QPushButton("Start Box " + str(self.box_id))
        control_start_all_button = QtWidgets.QPushButton("Start All")
        control_start_group_button = QtWidgets.QPushButton("Update Box" + str(self.box_id))
        control_abort_button = QtWidgets.QPushButton("Abort Box " + str(self.box_id))
        control_abort_all_button = QtWidgets.QPushButton("Abort All")

        # Adding the buttons to the layout
        control_form_layout.addRow("Current Status: ", self.current_state_show)
        control_form_layout.addRow("Generation", self.control_id_box)
        control_form_layout.addRow("Concentration", self.concentrate_box)
        control_form_layout2.addRow("Start Box " + str(self.box_id), control_start_button)
        control_form_layout2.addRow("Start All", control_start_all_button)
        control_form_layout2.addRow("Abort", control_abort_button)
        control_form_layout2.addRow("Abort All", control_abort_all_button)
        control_form_layout2.addRow("Update Box " + str(self.box_id), control_start_group_button)

        # slots
        self.control_id_box.textChanged.connect(self.control_id_slot)
        self.concentrate_box.textChanged.connect(self.concentrate_slot)
        control_start_button.clicked.connect(self.button_one_slot)
        control_start_all_button.clicked.connect(self.button_two_slot)
        control_start_group_button.clicked.connect(self.update_settings_slot)
        control_abort_button.clicked.connect(self.button_four_slot)
        control_abort_all_button.clicked.connect(self.abort_all_slot)
        control_form_layout.setHorizontalSpacing(100)
        control_form_layout.setVerticalSpacing(50)
        control_form_layout2.setHorizontalSpacing(110)
        control_form_layout2.setVerticalSpacing(30)
        dumb_button = QtWidgets.QPushButton()
        holder_layout = QtWidgets.QVBoxLayout()
        smaller_holder = QtWidgets.QVBoxLayout()
        horz_holder = QtWidgets.QHBoxLayout()
        smaller_holder.addLayout(control_form_layout)
        smaller_holder.addSpacing(50)
        horz_holder.addSpacing(260)
        horz_holder.addLayout(control_form_layout2)
        control_box_layout.addWidget(dumb_button)
        holder_layout.addLayout(smaller_holder)
        holder_layout.addLayout(horz_holder)
        control_tab_widget.setLayout(holder_layout)
        dumb_button.hide()

    # control slots
    def control_id_slot(self):
        self.settings_flag = True
        self.settings.setValue(("control_number/box_id_" + str(self.box_id)), self.control_id_box.toPlainText())

    def concentrate_slot(self):
        self.settings_flag = True
        self.settings.setValue(("concentrate/box_id_" + str(self.box_id)), self.concentrate_box.toPlainText())

    def update_status_label(self, status):
        self.current_state_label = self.current_state_strings[status]
        self.current_state_show.setText(self.current_state_label)

    def button_one_slot(self):
        # Start this box, if settings are ready
        if self.settings_flag:
            msg = QtWidgets.QMessageBox()
            msg.setInformativeText("Please update Shuttlebox " + str(self.box_id) + " before starting.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setModal(True)
            msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msg.exec()
        else:
            if self.current_state != 0:
                m = QtWidgets.QMessageBox()
                m.setInformativeText("Error: Cannot update Shuttlebox while trial is running.")
                msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                msg.setModal(True)
                m.exec()
            elif self.control_id_box.toPlainText() == "ENTER GENERATION":
                msg = QtWidgets.QMessageBox()
                msg.setInformativeText("Please enter a generation ID.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                msg.setModal(True)
                msg.exec()
            elif self.concentrate_box.toPlainText() == "ENTER CONCENTRATE":
                msg = QtWidgets.QMessageBox()
                msg.setInformativeText("Please enter a concentration.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                msg.setModal(True)
                msg.exec()
            else:
                self.box_handler.send_data_init(self.box_id)
                self.send_to_box(self.box_id)
                self.send_to_box(",")
                self.send_to_box("250")
                print("Start pushed")
                self.msleep(50)

    def button_two_slot(self):
        # Signal all the boxes to start via the BoxHandler
        BoxHandler.start_all_boxes_manager = True
        BoxHandler.start_all_boxes(self.box_handler)
        print("Start all signal pushed")

    def abort_all_slot(self):
        # Signal all the boxes to abort via the BoxHandler
        BoxHandler.abort_all_boxes_manager = True
        BoxHandler.abort_all(self.box_handler)

    def button_four_slot(self):
        # abort this box
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("254")
        print("Abort pushed")
        self.msleep(50)

    def on_start_all_boxes(self):
        # This runs after getting the signal from BoxHandler to start all boxes (can be called from same thread)
        print("on start all " + str(self.box_id))

        ###############################################RESTORE THIS SECTION BEFORE LAUNCH###############################
        # if self.settings_flag:
        #     msg = QtWidgets.QMessageBox()
        #     msg.setInformativeText("Please update Shuttlebox " + str(self.box_id) + " before starting.")
        #     msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        #     msg.exec()
            # if self.control_id_box.toPlainText() == "ENTER GENERATION":
            #     msg = QtWidgets.QMessageBox()
            #     msg.setInformativeText("Please enter a generation ID for box " + str(self.box_id))
            #     msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            #     msg.exec()
            # elif self.concentrate_box.toPlainText() == "ENTER CONCENTRATE":
            #     msg = QtWidgets.QMessageBox()
            #     msg.setInformativeText("Please enter a concentration for box " + str(self.box_id))
            #     msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            #     msg.exec()
            # elif self.current_state != 0:
            #     m = QtWidgets.QMessageBox()
            #     m.setInformativeText("Error: Cannot update Shuttlebox while trial is running.")
            #     m.exec()
            # else:
            #     self.results_class.results_init(self.box_id)
            #     self.send_to_box(self.box_id)
            #     self.send_to_box(",")
            #     self.send_to_box("250")
            #     print("Start all")
            #     self.msleep(50)

        ######################This section is to test results behavior, remove before launch!############
        self.counter = self.counter + 1
        self.results = [int(self.counter), 18, 28, 38, 48, 58, 68, 78, 88]
        print(self.counter)
        if int(self.counter) == int(self.settings.value(("boxes/box_id_" + str(self.box_id) + "/n_of_trials"))):
            self.counter = 0
        self.box_handler.send_data(self.results, self.box_id)

    def on_abort_all_boxes(self):
        # This runs after getting the signal from BoxHandler to abort all boxes (can be called from same thread)
        print("abort all from " + str(self.box_id))
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("248")
        print("Abort all")
        self.msleep(50)

    def on_stop_all_threads_slot(self):
        self.should_run = False



