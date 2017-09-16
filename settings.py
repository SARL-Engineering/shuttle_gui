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
        self.load_settings()

    @staticmethod
    def setup_settings():
        QtCore.QCoreApplication.setOrganizationName("OSU SARL")
        QtCore.QCoreApplication.setOrganizationDomain("ehsc.oregonstate.edu/sarl")
        QtCore.QCoreApplication.setApplicationName("Pick And Plate")

    def load_settings(self):
        self.settings.setFallbacksEnabled(False)
        self.settings.setValue("boxes/test", 20)
        print("settings init")
        print("test", self.settings.value("boxes/test"))
        for box in range(0, 48):
            self.settings.setValue(("boxes/box_id_" + str(box) + "/n_of_trials"), box)
            print(self.settings.value("boxes/box_id_" + str(box) + "/n_of_trials"), int)

