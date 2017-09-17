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
        self.boxes_configs_box_array = []
        self.boxes_configs_array = []
        self.load_settings()

    @staticmethod
    def setup_settings():
        QtCore.QCoreApplication.setOrganizationName("OSU SARL")
        QtCore.QCoreApplication.setOrganizationDomain("ehsc.oregonstate.edu/sarl")
        QtCore.QCoreApplication.setApplicationName("Shuttlebox Behavior System")

    def load_settings(self):
        self.settings.setFallbacksEnabled(False)
        self.settings.setValue("boxes/test", 20)
        print("settings init")
        print("test", self.settings.value("boxes/test"))
        #self.settings.clear()
        self.boxes_configs_array.append("0 spot")
        for box in range(1, 48):
            self.settings.setValue(("control_number/box_id_" + str(box)), self.settings.value((
                "control_number/box_id_" + str(box)), "ENTER CONTROL"))
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

            #make the array for sending settings to arduinos
            self.boxes_configs_box_array = [self.settings.value(("boxes/box_id_" + str(box) + "/n_of_trials"), box),
                                            self.settings.value(("boxes/box_id_" + str(box) + "selection_mode"), 1),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/settle_time"), 600),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/trial_duration"), 24),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/seek_time"), 12),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/trial_settle_time"), 12),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/fault_trials_percent"), 16),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/fault_out_side"), 8),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/fault_out_percent"), 95),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/shock_voltage"), 20),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/shock_interval"), 500),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/shock_duration"), 50),
                                            self.settings.value(("boxes/box_id_" + str(box) + "/success_trials"), 5)]
            self.boxes_configs_array.append(self.boxes_configs_box_array)

    def send_box_configs(self, box_id):
        return self.boxes_configs_array[box_id]
