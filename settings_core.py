from PyQt5 import QtCore, QtWidgets
import serial
from Framework.BoxHandlerCore import BoxHandler


class ShuttleSettings(QtCore.QObject):
    def __init__(self, main_window):
        QtCore.QObject.__init__(self)

        # ########## Reference to highest level window ##########
        self.main_window = main_window
        self.setup_settings()
        self.settings = QtCore.QSettings()
        ##############Arrays for exporting the settings #########
        self.boxes_configs_box_array = []
        self.boxes_configs_array = []
        self.boxes_settle_lights_box_array = []
        self.boxes_settle_lights_array = []
        self.boxes_trial_lights_box_array = []
        self.boxes_trial_lights_array = []
        self.boxes_start_lights_box_array = []
        self.boxes_start_lights_array = []
        #############run#########################################
        self.settings.setFallbacksEnabled(False)
        #self.settings.clear()
        self.load_settings()
        self.load_settle_lights()
        self.load_trial_lights()
        self.load_start_lights()

    @staticmethod
    def setup_settings():
        QtCore.QCoreApplication.setOrganizationName("OSU SARL")
        QtCore.QCoreApplication.setOrganizationDomain("ehsc.oregonstate.edu/sarl")
        QtCore.QCoreApplication.setApplicationName("Shuttlebox Behavior System")

    def load_settings(self):
        self.boxes_configs_array.append("0 spot")
        for box in range(1, 48):
            self.settings.setValue(("control_number/box_id_" + str(box)), self.settings.value((
                "control_number/box_id_" + str(box)), "ENTER GENERATION"))
            self.settings.setValue(("concentrate/box_id_" + str(box)), self.settings.value(("concentrate/box_id_" +
                                                                                           str(box)), "ENTER CONCENTRATE"))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/n_of_trials"), self.settings.value((
                "boxes/box_id_" + str(box) + "/n_of_trials"), box))
            self.settings.setValue(("boxes/box_id_" + str(box) + "selection_mode"), self.settings.value((
                "boxes/box_id_" + str(box) + "selection_mode"), 1))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/settle_time"), self.settings.value((
                "boxes/box_id_" + str(box) + "/settle_time"), 600))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_duration"), self.settings.value((
                "boxes/box_id_" + str(box) + "/trial_duration"), 24))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/seek_time"), self.settings.value((
                "boxes/box_id_" + str(box) + "/seek_time"), 12))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_settle_time"), self.settings.value((
                "boxes/box_id_" + str(box) + "/trial_settle_time"), 12))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_trials_percent"), self.settings.value((
                "boxes/box_id_" + str(box) + "/fault_trials_percent"), 16))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_side"), self.settings.value((
                "boxes/box_id_" + str(box) + "/fault_out_side"), 8))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_percent"), self.settings.value((
                "boxes/box_id_" + str(box) + "/fault_out_percent"), 95))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_voltage"), self.settings.value((
                "boxes/box_id_" + str(box) + "/shock_voltage"), 20))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_interval"), self.settings.value((
                "boxes/box_id_" + str(box) + "/shock_interval"), 500))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_duration"), self.settings.value((
                "boxes/box_id_" + str(box) + "/shock_duration"), 50))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/success_trials"), self.settings.value((
                "boxes/box_id_" + str(box) + "/success_trials"), 5))

            #make the array for sending configs to arduinos
            self.boxes_configs_box_array = [self.settings.value(("boxes/box_id_" + str(box) + "/n_of_trials"), box),
                                            self.settings.value(("boxes/box_id_" + str(box) + "selection_mode"), 1),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/settle_time"), 600),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/trial_duration"), 24),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/seek_time"), 12),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/trial_settle_time"),
                                                                12),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/fault_trials_percent"),
                                                                16),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/fault_out_side"), 8),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/fault_out_percent"),
                                                                95),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/shock_voltage"), 20),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/shock_interval"), 500),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/shock_duration"), 50),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/success_trials"), 5)]
            self.boxes_configs_array.append(self.boxes_configs_box_array)

    def send_box_configs(self, box_id):
        return self.boxes_configs_array[box_id]

    def load_settle_lights(self):
        self.boxes_settle_lights_array.append("0 spot")
        for box in range(1, 48):
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_pattern"), self.settings.value((
                "lights/settle_lights/box_id_" + str(box) + "right_pattern"), 4))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_pattern"), self.settings.value((
                "lights/settle_lights/box_id_" + str(box) + "left_pattern"), 8))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "right_side_color"),
                                                       173))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "left_side_color"),
                                                       120))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "right_side_bright")
                                                       , 255))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "left_side_bright"),
                                                       255))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "right_side_sat"),
                                                       100))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "left_side_sat"),
                                                       100))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "right_back_color"),
                                                       200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "left_back_color"),
                                                       150))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "right_back_bright")
                                                       , 200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "left_back_bright"),
                                                       200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "right_back_sat"),
                                                       200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box) + "left_back_sat"),
                                                       200))
            self.boxes_settle_lights_box_array = [self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "right_pattern"), 4),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "left_pattern"), 7),
                                                  self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                    str(box) + "right_side_color"), 100)
                                                               , 0, 360, 0, 255),
                                                  self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                    str(box) + "left_side_color"), 100)
                                                               , 0, 360, 0, 255),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "right_side_bright"), 100),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "left_side_bright"), 100),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "right_side_sat"), 100),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "left_side_sat"), 100),
                                                  self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                    str(box) + "right_back_color"), 100)
                                                               , 0, 360, 0, 255),
                                                  self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                    str(box) + "left_back_color"), 100)
                                                               , 0, 360, 0, 255),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "right_back_bright"), 200),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "left_back_bright"), 200),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "right_back_sat"), 200),
                                                  self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                       "left_back_sat"), 200),
                                                  200, 225, 255, 0, 255, 200, 0, 1
                                                  ]
            self.boxes_settle_lights_array.append(self.boxes_settle_lights_box_array)

    def send_settle_lights(self, box_id):
        return self.boxes_settle_lights_array[box_id]

    def load_trial_lights(self):

        self.boxes_trial_lights_array.append("0 spot")
        for box in range (1, 48):
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_pattern"), self.settings.value((
                "lights/trial_lights/box_id_" + str(box) + "right_pattern"), 4))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_pattern"), self.settings.value((
                "lights/trial_lights/box_id_" + str(box) + "left_pattern"), 8))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "right_side_color"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "left_side_color"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "right_side_bright")
                                                       , 100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "left_side_bright"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "right_side_sat"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "left_side_sat"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "right_back_color"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "left_back_color"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "right_back_bright")
                                                       , 200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "left_back_bright"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "right_back_sat"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box) + "left_back_sat"),
                                                       200))

            self.boxes_trial_lights_box_array = [self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                     "right_pattern"), 4),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "left_pattern"), 4),
                                                 self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                                   str(box) + "right_side_color"), 100)
                                                              , 0, 360, 0, 255),
                                                 self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                                   str(box) + "left_side_color"), 100)
                                                              , 0, 360, 0, 255),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "right_side_bright"), 100),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "left_side_bright"), 100),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "right_side_sat"), 100),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "left_side_sat"), 100),
                                                 self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                                   str(box) + "right_back_color"), 100)
                                                              , 0, 360, 0, 255),
                                                 self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                                   str(box) + "left_back_color"), 100)
                                                              , 0, 360, 0, 255),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "right_back_bright"), 200),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "left_back_bright"), 200),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "right_back_sat"), 200),
                                                 self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                      "left_back_sat"), 200), 200, 225, 255, 0, 255,
                                                 200, 0, 1]
            self.boxes_trial_lights_array.append(self.boxes_trial_lights_box_array)

    def send_trial_lights(self, box_id):
        return self.boxes_trial_lights_array[box_id]

    def load_start_lights(self):
        self.boxes_start_lights_array.append("0 spot")
        for box in range(1, 48):
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_pattern"), self.settings.value((
                "lights/start_lights/box_id_" + str(box) + "right_pattern"), 4))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_pattern"), self.settings.value((
                "lights/start_lights/box_id_" + str(box) + "left_pattern"), 8))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "right_side_color"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "left_side_color"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "right_side_bright")
                                                       , 100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "left_side_bright"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "right_side_sat"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "left_side_sat"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "right_back_color"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "left_back_color"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "right_back_bright")
                                                       , 200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "left_back_bright"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "right_back_sat"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box) + "left_back_sat"),
                                                       200))

            self.boxes_start_lights_box_array = [self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                      "right_pattern"), 4),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                      "left_pattern"), 4),
                                                 self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                                   str(box) + "right_side_color"), 100),
                                                              0, 360, 0, 255),
                                                 self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                                   str(box) + "left_side_color"), 100),
                                                              0, 360, 0, 255),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "right_side_bright"), 100),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "left_side_bright"), 100),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "right_side_sat"), 100),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "left_side_sat"), 100),
                                                 self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                                   str(box) + "right_back_color"), 100),
                                                              0, 360, 0, 255),
                                                 self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                                   str(box) + "left_back_color"), 100),
                                                              0, 360, 0, 255),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "right_back_bright"), 200),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                      "left_back_bright"), 200),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "right_back_sat"), 200),
                                                 self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                     "left_back_sat"), 200), 200, 225, 255, 0, 255,
                                                 200, 0, 1]
            self.boxes_start_lights_array.append(self.boxes_start_lights_box_array)

    def send_start_lights(self, box_id):
        return self.boxes_start_lights_array[box_id]

    def scaling(self, Input, InputLow, InputHigh, OutputLow, OutputHigh):
        Result = int(((Input - InputLow) / (InputHigh - InputLow)) * (OutputHigh - OutputLow) + OutputLow)
        return Result

    def restore_all_defaults(self):
        for box in range(1, 48):
            ##############Control######################
            self.settings.setValue(("control_number/box_id_" + str(box)), "ENTER GENERATION")
            self.settings.setValue(("concentrate/box_id_" + str(box)), "ENTER CONCENTRATE")
            self.settings.setValue(("boxes/box_id_" + str(box) + "/n_of_trials"), box)
            self.settings.setValue(("boxes/box_id_" + str(box) + "selection_mode"), 1)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/settle_time"), 600)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_duration"), 24)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/seek_time"), 12)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_settle_time"), 12)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_trials_percent"), 16)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_side"), 8)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_percent"), 95)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_voltage"), 20)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_interval"), 500)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_duration"), 50)
            self.settings.setValue(("boxes/box_id_" + str(box) + "/success_trials"), 5)

            ########################Settle Lights ############################################
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_pattern"), 4)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_pattern"), 8)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_color"), 173)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_color"), 120)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_bright"), 255)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_bright"), 255)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_sat"), 100)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_sat"), 100)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_color"), 200)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_color"), 150)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_bright"), 200)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_bright"), 200)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_sat"), 200)
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_sat"), 200)

            ########################Trial Lights ####################################################
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_pattern"), 4)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_pattern"), 8)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_color"), 100)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_color"), 100)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_bright"), 100)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_bright"), 100)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_sat"), 100)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_sat"), 100)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_color"), 200)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_color"), 200)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_bright") , 200)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_bright"), 200)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_sat"), 200)
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_sat"), 200)

            ########################Start Lights######################################################
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_pattern"), 4)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_pattern"), 8)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_color"), 100)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_color"), 100)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_bright"), 100)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_bright"), 100)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_sat"), 100)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_sat"), 100)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_color"), 200)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_color"), 200)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_bright"), 200)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_bright"), 200)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_sat"), 200)
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_sat"), 200)

    def restore_box_defaults(self, box):
        ##############Control######################
        self.settings.setValue(("control_number/box_id_" + str(box)), "ENTER GENERATION")
        self.settings.setValue(("concentrate/box_id_" + str(box)), "ENTER CONCENTRATE")
        self.settings.setValue(("boxes/box_id_" + str(box) + "/n_of_trials"), box)
        self.settings.setValue(("boxes/box_id_" + str(box) + "selection_mode"), 1)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/settle_time"), 600)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_duration"), 24)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/seek_time"), 12)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_settle_time"), 12)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_trials_percent"), 16)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_side"), 8)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_percent"), 95)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_voltage"), 20)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_interval"), 500)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_duration"), 50)
        self.settings.setValue(("boxes/box_id_" + str(box) + "/success_trials"), 5)

        ########################Settle Lights ############################################
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_pattern"), 4)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_pattern"), 4)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_color"), 100)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_color"), 100)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_bright"), 100)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_bright"), 100)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_sat"), 100)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_sat"), 100)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_color"), 200)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_color"), 200)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_bright"), 200)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_bright"), 200)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_sat"), 200)
        self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_sat"), 200)

        ########################Trial Lights ####################################################
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_pattern"), 4)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_pattern"), 4)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_color"), 100)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_color"), 100)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_bright"), 100)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_bright"), 100)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_sat"), 100)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_sat"), 100)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_color"), 200)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_color"), 200)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_bright"), 200)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_bright"), 200)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_sat"), 200)
        self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_sat"), 200)

        ########################Start Lights######################################################
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_pattern"), 4)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_pattern"), 4)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_color"), 100)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_color"), 100)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_bright"), 100)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_bright"), 100)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_sat"), 100)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_sat"), 100)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_color"), 200)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_color"), 200)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_bright"), 200)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_bright"), 200)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_sat"), 200)
        self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_sat"), 200)

    def update_settings(self, box):

        self.boxes_configs_box_array = [self.settings.value(("boxes/box_id_" + str(box) + "/n_of_trials"), box),
                                        self.settings.value(("boxes/box_id_" + str(box) + "selection_mode"), 1),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/settle_time"), 600),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/trial_duration"), 24),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/seek_time"), 12),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/trial_settle_time"),
                                                            12),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/fault_trials_percent"),
                                                            16),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/fault_out_side"), 8),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/fault_out_percent"),
                                                            95),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/shock_voltage"), 20),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/shock_interval"), 500),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/shock_duration"), 50),
                                        self.settings.value(("boxes/box_id_" + str(box) + "/success_trials"), 5)]
        self.boxes_configs_array[box] = self.boxes_configs_box_array

        self.boxes_settle_lights_box_array = [self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "right_pattern"), 4),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "left_pattern"), 7),
                                              self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                str(box) + "right_side_color"), 100)
                                                           , 0, 360, 0, 255),
                                              self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                str(box) + "left_side_color"), 100)
                                                           , 0, 360, 0, 255),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "right_side_bright"), 100),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "left_side_bright"), 100),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "right_side_sat"), 100),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "left_side_sat"), 100),
                                              self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                str(box) + "right_back_color"), 100)
                                                           , 0, 360, 0, 255),
                                              self.scaling(self.settings.value(("lights/settle_lights/box_id_" +
                                                                                str(box) + "left_back_color"), 100)
                                                           , 0, 360, 0, 255),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "right_back_bright"), 200),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "left_back_bright"), 200),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "right_back_sat"), 200),
                                              self.settings.value(("lights/settle_lights/box_id_" + str(box) +
                                                                   "left_back_sat"), 200),
                                              200, 225, 255, 0, 255, 200, 0, 1
                                              ]
        self.boxes_settle_lights_array[box] = self.boxes_settle_lights_box_array

        self.boxes_trial_lights_box_array = [self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "right_pattern"), 4),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "left_pattern"), 4),
                                             self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                               str(box) + "right_side_color"), 100)
                                                          , 0, 360, 0, 255),
                                             self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                               str(box) + "left_side_color"), 100)
                                                          , 0, 360, 0, 255),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "right_side_bright"), 100),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "left_side_bright"), 100),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "right_side_sat"), 100),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "left_side_sat"), 100),
                                             self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                               str(box) + "right_back_color"), 100)
                                                          , 0, 360, 0, 255),
                                             self.scaling(self.settings.value(("lights/trial_lights/box_id_" +
                                                                               str(box) + "left_back_color"), 100)
                                                          , 0, 360, 0, 255),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "right_back_bright"), 200),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "left_back_bright"), 200),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "right_back_sat"), 200),
                                             self.settings.value(("lights/trial_lights/box_id_" + str(box) +
                                                                  "left_back_sat"), 200), 200, 225, 255, 0, 255,
                                             200, 0, 1]
        self.boxes_trial_lights_array[box] = self.boxes_trial_lights_box_array

        self.boxes_start_lights_box_array = [self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "right_pattern"), 4),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "left_pattern"), 4),
                                             self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                               str(box) + "right_side_color"), 100),
                                                          0, 360, 0, 255),
                                             self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                               str(box) + "left_side_color"), 100),
                                                          0, 360, 0, 255),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "right_side_bright"), 100),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "left_side_bright"), 100),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "right_side_sat"), 100),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "left_side_sat"), 100),
                                             self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                               str(box) + "right_back_color"), 100),
                                                          0, 360, 0, 255),
                                             self.scaling(self.settings.value(("lights/start_lights/box_id_" +
                                                                               str(box) + "left_back_color"), 100),
                                                          0, 360, 0, 255),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "right_back_bright"), 200),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "left_back_bright"), 200),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "right_back_sat"), 200),
                                             self.settings.value(("lights/start_lights/box_id_" + str(box) +
                                                                  "left_back_sat"), 200), 200, 225, 255, 0, 255,
                                             200, 0, 1]
        self.boxes_start_lights_array = self.boxes_start_lights_box_array

    def apply_all_settings(self, box_id):
        for box in range(1, 48):
            self.settings.setValue(("control_number/box_id_" + str(box)), self.settings.value((
                "control_number/box_id_" + str(box_id)), "ENTER GENERATION"))
            self.settings.setValue(("concentrate/box_id_" + str(box)), self.settings.value(("concentrate/box_id_" +
                                                                                           str(box_id)), "ENTER CONCENTRATE"))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/n_of_trials"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/n_of_trials"), box))
            self.settings.setValue(("boxes/box_id_" + str(box) + "selection_mode"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "selection_mode"), 1))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/settle_time"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/settle_time"), 600))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_duration"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/trial_duration"), 24))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/seek_time"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/seek_time"), 12))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/trial_settle_time"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/trial_settle_time"), 12))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_trials_percent"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/fault_trials_percent"), 16))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_side"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/fault_out_side"), 8))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/fault_out_percent"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/fault_out_percent"), 95))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_voltage"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/shock_voltage"), 20))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_interval"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/shock_interval"), 500))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/shock_duration"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/shock_duration"), 50))
            self.settings.setValue(("boxes/box_id_" + str(box) + "/success_trials"), self.settings.value((
                "boxes/box_id_" + str(box_id) + "/success_trials"), 5))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_pattern"), self.settings.value((
                "lights/settle_lights/box_id_" + str(box) + "right_pattern"), 4))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_pattern"), self.settings.value((
                "lights/settle_lights/box_id_" + str(box_id) + "left_pattern"), 8))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "right_side_color"),
                                                       173))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "left_side_color"),
                                                       120))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "right_side_bright")
                                                       , 255))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "left_side_bright"),
                                                       255))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_side_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "right_side_sat"),
                                                       100))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_side_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "left_side_sat"),
                                                       100))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "right_back_color"),
                                                       200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_color"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "left_back_color"),
                                                       150))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "right_back_bright")
                                                       , 200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_bright"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "left_back_bright"),
                                                       200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "right_back_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "right_back_sat"),
                                                       200))
            self.settings.setValue(("lights/settle_lights/box_id_" + str(box) + "left_back_sat"),
                                   self.settings.value(("lights/settle_lights/box_id_" + str(box_id) + "left_back_sat"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_pattern"), self.settings.value((
                "lights/trial_lights/box_id_" + str(box_id) + "right_pattern"), 4))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_pattern"), self.settings.value((
                "lights/trial_lights/box_id_" + str(box_id) + "left_pattern"), 8))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "right_side_color"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "left_side_color"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "right_side_bright")
                                                       , 100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "left_side_bright"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_side_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "right_side_sat"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_side_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "left_side_sat"),
                                                       100))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "right_back_color"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_color"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "left_back_color"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "right_back_bright")
                                                       , 200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_bright"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "left_back_bright"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "right_back_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "right_back_sat"),
                                                       200))
            self.settings.setValue(("lights/trial_lights/box_id_" + str(box) + "left_back_sat"),
                                   self.settings.value(("lights/trial_lights/box_id_" + str(box_id) + "left_back_sat"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_pattern"), self.settings.value((
                "lights/start_lights/box_id_" + str(box_id) + "right_pattern"), 4))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_pattern"), self.settings.value((
                "lights/start_lights/box_id_" + str(box_id) + "left_pattern"), 8))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "right_side_color"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "left_side_color"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "right_side_bright")
                                                       , 100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "left_side_bright"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_side_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "right_side_sat"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_side_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "left_side_sat"),
                                                       100))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "right_back_color"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_color"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "left_back_color"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "right_back_bright")
                                                       , 200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_bright"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "left_back_bright"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "right_back_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "right_back_sat"),
                                                       200))
            self.settings.setValue(("lights/start_lights/box_id_" + str(box) + "left_back_sat"),
                                   self.settings.value(("lights/start_lights/box_id_" + str(box_id) + "left_back_sat"),
                                                       200))

