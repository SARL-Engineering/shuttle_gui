from PyQt5 import QtCore, QtWidgets, QtGui
import serial
from Framework.BoxHandlerCore import BoxHandler
from settings_core import ShuttleSettings


class SerialThread(QtCore.QThread):
    change_label_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_window, box_handler, comport_string):
        super(SerialThread, self).__init__()

        self.main_window = main_window
        self.box_handler = box_handler
        self.comport_string = comport_string

        # Gui Object References
        self.id_list_widget = self.main_window.id_list_widget  # type: QtWidgets.QListWidget
        self.in_buffer = ""
        self.should_run = True
        self.n_of_trials_flag = None
        self.current_state = None
        self.current_state_label = None
        self.current_state_strings = ["Wait for Start", "Test Start", "Settle Period", "Inter Trial", "Trial Start",
                                      "Trial Seek", "Trial Shock", "Trial End", "Abort", "Test End"]
        self.pattern_list = ["Heart", "Big X", "Big O", "Horizontal Lines", "Vertical Lines", "Diagonal Lines",
                             "Big Line", "Small Box", "Corners"]
        self.current_tab = 0
        self.tab_flag = 0
        self.update_flag = None
        self.settings_flag = False
        self.arduino = serial.Serial(comport_string, 9600, bytesize=8, stopbits=1, timeout=None)
        self.box_id_found_flag = False
        self.box_id = None
        self.box_tab_widget = None  # type: QtWidgets.QTabWidget
        self.show_box_tab_widget_flag = False
        self.tab_widget_w = self.main_window.tab_widget_widget
        self.__connect_signals_to_slots()
        self.settings = QtCore.QSettings()
        self.settings_core = ShuttleSettings(main_window)
        self.start()

    def __connect_signals_to_slots(self):
        self.main_window.id_list_widget.currentRowChanged.connect(self.on_current_box_id_changed_slot)
        self.main_window.stop_all_threads.connect(self.on_stop_all_threads_slot)
        self.box_handler.start_all_boxes_signal.connect(self.on_start_all_boxes)

    def run(self):

        while self.should_run:

                if self.arduino.inWaiting():
                    in_byte = self.arduino.read().decode("utf-8")
                    self.in_buffer += in_byte

                    if in_byte == "\n":
                        if "show: " in self.in_buffer:
                            self.box_tab_widget.setVisible(True)
                        if "u: " in self.in_buffer:
                            self.update_flag = 1
                        if "Box ID: " in self.in_buffer:
                            self.box_id_found_flag = True
                            self.box_id = int(self.in_buffer.split(": ")[1])
                            print("Box ID: " + str(self.box_id) + " found")
                        if "s: " in self.in_buffer:
                            self.current_state = int(self.in_buffer.split(": ")[1])
                            print("STATE = " + str(self.current_state))
                            self.update_status_label(int(self.current_state))
                        if "x: " in self.in_buffer:
                            print("sending configs to box " + str(self.box_id))
                            self.settings_core.update_settings(self.box_id)
                            self.send_to_box(self.settings_core.send_box_configs(self.box_id))
                            self.send_to_box(self.settings_core.send_settle_lights(self.box_id))
                            self.send_to_box(self.settings_core.send_trial_lights(self.box_id))
                            self.send_to_box(self.settings_core.send_start_lights(self.box_id))
                            # self.send_to_box(" ")
                            # self.send_to_box("50,1,600,24,12,12,16,8,95,20,500,50,5")
                            # self.send_to_box("4,8,100,150,255,0,255,0,50,75,255,0,255,0,200,225,255,0,255,200,0,1")
                            # self.send_to_box("7,3,200,15,12,255,10,255,50,75,0,255,0,255,200,225,0,255,255,200,1,0")
                            # self.send_to_box("7,3,200,15,12,255,10,255,50,75,0,255,0,255,200,225,0,255,255,200,1,0")
                        print(self.in_buffer)
                        self.in_buffer = ""

                self.msleep(50)
                self.arduino.flush()

    def send_to_box(self, message):
        self.arduino.write(bytes(str(message), "utf-8"))

    def make_box_tab_widget(self, parent):
        self.box_tab_widget = QtWidgets.QTabWidget(parent)
        self.make_control_tab()
        self.make_settings_tab()
        self.make_lights_tab()
        self.make_admin_tab()
        if self.tab_flag == 0:
            self.box_tab_widget.setVisible(False)
        return self.box_tab_widget

    def make_admin_tab(self):
    ###############Admin Tab#################################################################
        admin_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(admin_tab_widget, "Admin")
        admin_layout = QtWidgets.QFormLayout()
        self.restore_all_def_button = QtWidgets.QPushButton("THINK FIRST")
        self.restore_all_def_button.clicked.connect(self.restore_all_def_slot)
        self.restore_def_button = QtWidgets.QPushButton("MOSTLY SAFE")
        self.restore_def_button.clicked.connect(self.restore_def_slot)

        admin_layout.addRow("Restore defaults for Shuttlebox " + str(self.box_id), self.restore_def_button)
        admin_layout.addRow("Restore all defaults", self.restore_all_def_button)
        admin_tab_widget.setLayout(admin_layout)

    def restore_all_def_slot(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("Are you absolutely sure you want to restore the defaults for ALL Shuttleboxes?")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.RestoreDefaults | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret == QtWidgets.QMessageBox.RestoreDefaults:
            self.settings_core.restore_all_defaults()
            self.update_settings_slot()
            self.get_conf_settings()

    def restore_def_slot(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("Are you absolutely sure you want to restore the defaults for Shuttlebox " + str(self.box_id) +
                       "?")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.RestoreDefaults | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret == QtWidgets.QMessageBox.RestoreDefaults:
            self.settings_core.restore_box_defaults(self.box_id)
            self.update_settings_slot()
            self.get_conf_settings()

    ###############SETTINGS GUI #####################################################################

    def make_settings_tab(self):
        self.settings_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(self.settings_tab_widget, "Settings")
        settings_layout = QtWidgets.QFormLayout()
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
        settings_layout.addRow("Selection Mode (set to 1)", self.selection_box)
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
        settings_layout.addRow("Save Settings", self.update_button)

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

        self.settings_tab_widget.setLayout(settings_layout)
        ################SETTINGS SLOTS###################################################################################

    def get_conf_settings(self):
        # retrive the settings
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

    def n_of_trials_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/n_of_trials"), self.n_of_trials_box.value())

    def selection_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "selection_mode"), self.selection_box.value())

    def settle_time_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/settle_time"), self.settle_time_box.value())

    def trial_duration_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/trial_duration"),
                               self.trial_duration_box.value())

    def seek_time_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/seek_time"), self.seek_time_box.value())

    def trial_settle_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/trial_settle_time"),
                               self.trial_settle_box.value())

    def fault_side_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/fault_out_side"),
                               self.fault_side_box.value())

    def fault_out_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/fault_out_percent"),
                               self.fault_out_box.value())

    def shock_voltage_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/shock_voltage"),
                               self.shock_voltage_box.value())

    def shock_interval_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/shock_interval"),
                               self.shock_interval_box.value())

    def shock_duration_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/shock_duration"),
                               self.shock_duration_box.value())

    def success_trials_slot(self):
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/success_trials"),
                               self.success_trials_box.value())

    def update_settings_slot(self):
        msg = QtWidgets.QMessageBox()
        msg.setText("Please wait, updating settings (press OK now).....")
        self.box_tab_widget.setHidden(True)
        self.update_flag = 0
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("249")
        msg.exec()
        while self.update_flag == 0:
            pass
        msg_box = QtWidgets.QMessageBox()
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.setText("Settings Updated")
        msg_box.exec()
        self.box_tab_widget.setHidden(False)
        self.update_flag = 0

####################################LIGHTING GUI###########################################################
    def make_lights_tab(self):
        lights_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(lights_tab_widget, "Lights")
        lights_tab_layout = QtWidgets.QFormLayout()
        ##################SETTLE LIGHTS####################################################################
        ####make the buttons#####
        self.settle_lights_r_pattern_button = QtWidgets.QComboBox()
        self.settle_lights_r_pattern_button.insertItems(0, self.pattern_list)
        self.settle_lights_r_pattern_button.setCurrentIndex(self.settings.value("lights/settle_lights/box_id_" +
                                                                                str(self.box_id) + "right_pattern", int)
                                                            )
        self.settle_lights_l_pattern_button = QtWidgets.QComboBox()
        self.settle_lights_l_pattern_button.insertItems(0, self.pattern_list)
        self.settle_lights_l_pattern_button.setCurrentIndex(self.settings.value("lights/settle_lights/box_id_" +
                                                                                str(self.box_id) + "left_pattern", int))
        self.settle_lights_r_button = QtWidgets.QPushButton()
        self.settle_lights_l_button = QtWidgets.QPushButton()
        self.settle_lights_rb_button = QtWidgets.QPushButton()
        self.settle_lights_lb_button = QtWidgets.QPushButton()
        ####make the custom colors from the saved settings#####
        settle_lights_r_color = QtGui.QColor()
        settle_lights_l_color = QtGui.QColor()
        settle_lights_rb_color = QtGui.QColor()
        settle_lights_lb_color = QtGui.QColor()
        settle_lights_r_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                         "right_side_color", int),
                                     self.settings.value(("lights/settle_lights/box_id_" + str(self.box_id) +
                                                          "right_side_sat"), int), self.settings.value((
                                                            "lights/settle_lights/box_id_" + str(self.box_id) +
                                                            "right_side_bright"), int))
        settle_lights_rb_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                          "right_back_color", int), self.settings.value(
            ("lights/settle_lights/box_id_" + str(self.box_id) + "right_back_sat"), int), self.settings.value(
                ("lights/settle_lights/box_id_" + str(self.box_id) + "right_back_bright"), int))
        settle_lights_l_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                         "left_side_color", int),
                                     self.settings.value(("lights/settle_lights/box_id_" + str(self.box_id) +
                                                          "left_side_sat"), int), self.settings.value(
                ("lights/settle_lights/box_id_" + str(self.box_id) + "left_side_bright"), int))
        settle_lights_lb_color.setHsv(self.settings.value("lights/settle_lights/box_id_" + str(self.box_id) +
                                                          "left_back_color", int), self.settings.value(
            ("lights/settle_lights/box_id_" + str(self.box_id) + "left_back_sat"), int), self.settings.value(
                ("lights/settle_lights/box_id_" + str(self.box_id) + "left_back_bright"), int))

        ######add the buttons to the layout#######
        lights_tab_layout.addRow("Right Side Settle Pattern", self.settle_lights_r_pattern_button)
        lights_tab_layout.addRow("Right Side Settle Lights Color", self.settle_lights_r_button)
        lights_tab_layout.addRow("Right Side Settle Lights Background Color", self.settle_lights_rb_button)
        lights_tab_layout.addRow("Left Side Settle Pattern", self.settle_lights_l_pattern_button)
        lights_tab_layout.addRow("Left Side Settle Lights Color", self.settle_lights_l_button)
        lights_tab_layout.addRow("Left Side Settle Lights Background Color", self.settle_lights_lb_button)


        #############style#################
        self.settle_lights_r_button.setStyleSheet("QWidget { background-color: %s}" % settle_lights_r_color.name())
        self.settle_lights_rb_button.setStyleSheet("QWidget { background-color: %s}" % settle_lights_rb_color.name())
        self.settle_lights_l_button.setStyleSheet("QWidget { background-color: %s}" % settle_lights_l_color.name())
        self.settle_lights_lb_button.setStyleSheet("QWidget { background-color: %s}" % settle_lights_lb_color.name())

        ######connect the slots########
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

        #################################TRIAL LIGHTS#############################################################
        ####make the buttons#####
        self.trial_lights_r_pattern_button = QtWidgets.QComboBox()
        self.trial_lights_r_pattern_button.insertItems(0, self.pattern_list)
        self.trial_lights_r_pattern_button.setCurrentIndex(self.settings.value("lights/trial_lights/box_id_" +
                                                                                str(self.box_id) + "right_pattern", int)
                                                            )
        self.trial_lights_l_pattern_button = QtWidgets.QComboBox()
        self.trial_lights_l_pattern_button.insertItems(0, self.pattern_list)
        self.trial_lights_l_pattern_button.setCurrentIndex(self.settings.value("lights/trial_lights/box_id_" +
                                                                                str(self.box_id) + "left_pattern", int))
        self.trial_lights_r_button = QtWidgets.QPushButton()
        self.trial_lights_l_button = QtWidgets.QPushButton()
        self.trial_lights_rb_button = QtWidgets.QPushButton()
        self.trial_lights_lb_button = QtWidgets.QPushButton()
        ####make the custom colors from the saved settings#####
        trial_lights_r_color = QtGui.QColor()
        trial_lights_l_color = QtGui.QColor()
        trial_lights_rb_color = QtGui.QColor()
        trial_lights_lb_color = QtGui.QColor()
        trial_lights_r_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                         "right_side_color", int),
                                     self.settings.value(("lights/trial_lights/box_id_" + str(self.box_id) +
                                                          "right_side_sat"), int), self.settings.value((
                                                            "lights/trial_lights/box_id_" + str(self.box_id) +
                                                            "right_side_bright"), int))
        trial_lights_rb_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                          "right_back_color", int), self.settings.value(
            ("lights/trial_lights/box_id_" + str(self.box_id) + "right_back_sat"), int), self.settings.value(
                ("lights/trial_lights/box_id_" + str(self.box_id) + "right_back_bright"), int))
        trial_lights_l_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                         "left_side_color", int),
                                     self.settings.value(("lights/trial_lights/box_id_" + str(self.box_id) +
                                                          "left_side_sat"), int), self.settings.value(
                ("lights/trial_lights/box_id_" + str(self.box_id) + "left_side_bright"), int))
        trial_lights_lb_color.setHsv(self.settings.value("lights/trial_lights/box_id_" + str(self.box_id) +
                                                          "left_back_color", int), self.settings.value(
            ("lights/trial_lights/box_id_" + str(self.box_id) + "left_back_sat"), int), self.settings.value(
                ("lights/trial_lights/box_id_" + str(self.box_id) + "left_back_bright"), int))

        ######add the buttons to the layout#######
        lights_tab_layout.addRow("Right Side trial Pattern", self.trial_lights_r_pattern_button)
        lights_tab_layout.addRow("Right Side trial Lights Color", self.trial_lights_r_button)
        lights_tab_layout.addRow("Right Side trial Lights Background Color", self.trial_lights_rb_button)
        lights_tab_layout.addRow("Left Side trial Pattern", self.trial_lights_l_pattern_button)
        lights_tab_layout.addRow("Left Side trial Lights Color", self.trial_lights_l_button)
        lights_tab_layout.addRow("Left Side trial Lights Background Color", self.trial_lights_lb_button)


        #############style#################
        self.trial_lights_r_button.setStyleSheet("QWidget { background-color: %s}" % trial_lights_r_color.name())
        self.trial_lights_rb_button.setStyleSheet("QWidget { background-color: %s}" % trial_lights_rb_color.name())
        self.trial_lights_l_button.setStyleSheet("QWidget { background-color: %s}" % trial_lights_l_color.name())
        self.trial_lights_lb_button.setStyleSheet("QWidget { background-color: %s}" % trial_lights_lb_color.name())

        ######connect the slots########
        self.trial_lights_r_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "right_side_color",
                                                                                   "right_side_sat", "right_side_bright"
                                                                                   , self.trial_lights_r_button))
        self.trial_lights_rb_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "right_back_color",
                                                                                    "right_back_sat",
                                                                                    "right_back_bright",
                                                                                    self.trial_lights_rb_button))
        self.trial_lights_l_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "left_side_color",
                                                                                   "left_side_sat", "left_side_bright"
                                                                                   , self.trial_lights_l_button))
        self.trial_lights_lb_button.clicked.connect(lambda: self.color_select_slot("trial_lights", "left_back_color",
                                                                                    "left_back_sat", "left_back_bright"
                                                                                    , self.trial_lights_lb_button))
        self.trial_lights_r_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "trial_lights", "right_pattern", self.trial_lights_r_pattern_button.currentIndex()))
        self.trial_lights_l_pattern_button.currentIndexChanged.connect(lambda: self.pattern_select_slot(
            "trial_lights", "left_pattern", self.trial_lights_l_pattern_button.currentIndex()))

        ###################START LIGHTS ####################################################################
        ####make the buttons#####
        self.start_lights_r_pattern_button = QtWidgets.QComboBox()
        self.start_lights_r_pattern_button.insertItems(0, self.pattern_list)
        self.start_lights_r_pattern_button.setCurrentIndex(self.settings.value("lights/start_lights/box_id_" +
                                                                               str(self.box_id) + "right_pattern", int)
                                                           )
        self.start_lights_l_pattern_button = QtWidgets.QComboBox()
        self.start_lights_l_pattern_button.insertItems(0, self.pattern_list)
        self.start_lights_l_pattern_button.setCurrentIndex(self.settings.value("lights/start_lights/box_id_" +
                                                                               str(self.box_id) + "left_pattern", int))
        self.start_lights_r_button = QtWidgets.QPushButton()
        self.start_lights_l_button = QtWidgets.QPushButton()
        self.start_lights_rb_button = QtWidgets.QPushButton()
        self.start_lights_lb_button = QtWidgets.QPushButton()
        ####make the custom colors from the saved settings#####
        start_lights_r_color = QtGui.QColor()
        start_lights_l_color = QtGui.QColor()
        start_lights_rb_color = QtGui.QColor()
        start_lights_lb_color = QtGui.QColor()
        start_lights_r_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                        "right_side_color", int),
                                    self.settings.value(("lights/start_lights/box_id_" + str(self.box_id) +
                                                         "right_side_sat"), int), self.settings.value((
                "lights/start_lights/box_id_" + str(self.box_id) +
                "right_side_bright"), int))
        start_lights_rb_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                         "right_back_color", int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "right_back_sat"), int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "right_back_bright"), int))
        start_lights_l_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                        "left_side_color", int),
                                    self.settings.value(("lights/start_lights/box_id_" + str(self.box_id) +
                                                         "left_side_sat"), int), self.settings.value(
                ("lights/start_lights/box_id_" + str(self.box_id) + "left_side_bright"), int))
        start_lights_lb_color.setHsv(self.settings.value("lights/start_lights/box_id_" + str(self.box_id) +
                                                         "left_back_color", int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "left_back_sat"), int), self.settings.value(
            ("lights/start_lights/box_id_" + str(self.box_id) + "left_back_bright"), int))

        ######add the buttons to the layout#######
        lights_tab_layout.addRow("Right Side start Pattern", self.start_lights_r_pattern_button)
        lights_tab_layout.addRow("Right Side start Lights Color", self.start_lights_r_button)
        lights_tab_layout.addRow("Right Side start Lights Background Color", self.start_lights_rb_button)
        lights_tab_layout.addRow("Left Side start Pattern", self.start_lights_l_pattern_button)
        lights_tab_layout.addRow("Left Side start Lights Color", self.start_lights_l_button)
        lights_tab_layout.addRow("Left Side start Lights Background Color", self.start_lights_lb_button)

        #############style#################
        self.start_lights_r_button.setStyleSheet("QWidget { background-color: %s}" % start_lights_r_color.name())
        self.start_lights_rb_button.setStyleSheet("QWidget { background-color: %s}" % start_lights_rb_color.name())
        self.start_lights_l_button.setStyleSheet("QWidget { background-color: %s}" % start_lights_l_color.name())
        self.start_lights_lb_button.setStyleSheet("QWidget { background-color: %s}" % start_lights_lb_color.name())

        ######connect the slots########
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

        ##############Update button###############
        self.light_update_button = QtWidgets.QPushButton("UPDATE BOX" + str(self.box_id))
        lights_tab_layout.addRow("Save Settings", self.light_update_button)
        self.light_update_button.clicked.connect(self.update_settings_slot)

        #######set the layout in the tab##########
        lights_tab_widget.setLayout(lights_tab_layout)

    def color_select_slot(self, lights, hue, sat, val, button):
        temp_colorbox = QtWidgets.QColorDialog()
        temp_color = temp_colorbox.getColor()
        button.setStyleSheet("QWidget { background-color: %s}" % temp_color.name())
        temp = temp_color.getHsv()
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + hue + ""), int(temp[0]))
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + sat + ""), int(temp[1]))
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + val + ""), int(temp[2]))

    def pattern_select_slot(self, lights, pat, button):
        print(lights, pat)
        self.settings.setValue(("lights/" + lights + "/box_id_" + str(self.box_id) + pat + ""),
                               button)

#################CONTROL TAB GUI ############################################################
    def make_control_tab(self):
        ##Setting the layout
        control_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(control_tab_widget, "Control " + str(self.box_id))
        control_form_layout = QtWidgets.QFormLayout()
        control_tab_widget.setLayout(control_form_layout)
        ##Creating the button instances
        self.current_state_show = QtWidgets.QLabel()
        self.current_state_show.setText(str(self.current_state_label))
        self.control_id_box = QtWidgets.QTextEdit()
        self.control_id_box.setText(self.settings.value(("control_number/box_id_" + str(self.box_id))))
        control_start_button = QtWidgets.QPushButton("Start")
        control_start_all_button = QtWidgets.QPushButton("Start All")
        control_start_group_button = QtWidgets.QPushButton("Save Settings")
        control_abort_button = QtWidgets.QPushButton("Abort")
        ##Adding the buttons to the layout
        control_form_layout.addRow("Current Status: ", self.current_state_show)
        control_form_layout.addRow("Control ID", self.control_id_box)
        control_form_layout.addRow("Start", control_start_button)
        control_form_layout.addRow("Start All", control_start_all_button)
        control_form_layout.addRow("Save Settings", control_start_group_button)
        control_form_layout.addRow("Abort", control_abort_button)
        ##slots
        self.control_id_box.textChanged.connect(self.control_id_slot)
        control_start_button.clicked.connect(self.button_one_slot)
        control_start_all_button.clicked.connect(self.button_two_slot)
        control_start_group_button.clicked.connect(self.update_settings_slot)
        control_abort_button.clicked.connect(self.button_four_slot)

###############################control functions################################################
    def control_id_slot(self):
        self.settings.setValue(("control_number/box_id_" + str(self.box_id)), self.control_id_box.toPlainText())

    def update_status_label(self, status):
        self.current_state_label = self.current_state_strings[status]
        self.current_state_show.setText(self.current_state_label)

    def start_all_boxes_slot(self):
        self.start_all_boxes_signal.emit()

    def button_one_slot(self):
        if self.control_id_box.toPlainText() == "ENTER CONTROL":
            print("Need control ID popup for " + str(self.box_id))
        else:
            self.send_to_box(self.box_id)
            self.send_to_box(",")
            self.send_to_box("250")
            print("Start pushed")
            self.msleep(50)

    def button_two_slot(self):
        BoxHandler.start_all_boxes_manager = True
        BoxHandler.starter(self.box_handler)
        print("Start all signal pushed")

    def button_three_slot(self):
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("252")
        print("Show Lights")
        self.msleep(50)

    def button_four_slot(self):
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("254")
        print("Abort pushed")
        self.msleep(50)

    def on_start_all_boxes(self):
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("250")
        self.msleep(50)

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

            layout.addWidget(self.make_box_tab_widget(self.tab_widget_w))
            self.id_list_widget.sortItems()
            self.tab_flag = 1

    def on_stop_all_threads_slot(self):
        self.should_run = False

    def scaling(self, Input, InputLow, InputHigh, OutputLow, OutputHigh):
        Result = int(((Input - InputLow) / (InputHigh - InputLow)) * (OutputHigh - OutputLow) + OutputLow)
        return Result

