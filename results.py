from PyQt5 import QtCore, QtWidgets, QtGui
import os
from settings_core import ShuttleSettings


class BoxResults(QtCore.QObject):

    def __init__(self):
        self.settings = QtCore.QSettings()
        self.param_array = []
        self.acceptSide = []
        self.seekSideSwaps = []
        self.numSideSwaps = []
        self.timeToAccept = []
        self.rejectTime = []
        self.acceptTime = []
        self.shockModeTime = []
        self.shockedTime = []
        self.counter = 0
        self.acceptSide_path = None
        self.seekSideSwaps_path = None
        self.numSideSwaps_path = None
        self.timeToAccept_path = None
        self.rejectTime_path = None
        self.acceptTime_path = None
        self.shockModeTime_path = None
        self.shockedTime_path = None

    def results_init(self, box_id):

        self.acceptSide = [self.settings.value("control_number/box_id_" + str(box_id)),
                           self.settings.value("concentrate/box_id_" + str(box_id)),  ("Shuttlebox_" + str(box_id) +
                                                                                       "_on_" +
                                                                                       QtCore.QDateTime.currentDateTime(
                                                                                       ).toString(QtCore.Qt.ISODate))]
        self.seekSideSwaps = [self.settings.value("control_number/box_id_" + str(box_id)),
                              self.settings.value("concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) +
                                                                                         "_on_" + QtCore.QDateTime.
                                                                                         currentDateTime().toString
                                                                                         (QtCore.Qt.ISODate))]
        self.numSideSwaps = [self.settings.value("control_number/box_id_" + str(box_id)),
                              self.settings.value("concentrate/box_id_" + str(box_id)), (
                              "Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.currentDateTime().toString(
                                  QtCore.Qt.ISODate))]
        self.timeToAccept = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value
        ("concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.currentDateTime(
        ).toString(QtCore.Qt.ISODate))]
        self.rejectTime = [self.settings.value("control_number/box_id_" + str(box_id)),
                           self.settings.value("concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + "_on_" +
                           QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))]
        self.acceptTime = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value
        ("concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" +
                                                QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))]
        self.shockModeTime = [self.settings.value("control_number/box_id_" + str(box_id)),
                              self.settings.value("concentrate/box_id_" + str(box_id)), (
                              "Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.currentDateTime().toString(
                                  QtCore.Qt.ISODate))]
        self.shockedTime = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value
        ("concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" +
                                                QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))]

        self.acceptSide_path = ("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)) + "/acceptSide")
        if not os.path.isdir(self.acceptSide_path):
            os.makedirs(self.acceptSide_path)

    def results_to_array(self, results_array, box_id):
        self.acceptSide.append(results_array[0])
        print(self.acceptSide)
        m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        print("n of trials = ", m)
        if int(m) == int(results_array[0]):
            self.acceptSide[0] = self.settings.value("control_number/box_id_" + str(box_id))
            self.acceptSide[1] = self.settings.value("concentrate/box_id_" + str(box_id))
            self.acceptSide[2] = ("Shuttlebox_" + str(box_id) + "_on_" +
                                  QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
            print("writing string to file: ", self.acceptSide)
            file = open("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
                "control_number/box_id_" + str(box_id)) + "/acceptSide/acceptSide.txt", "a")
            for i in range(0, (3 + int(m))):
                if i == (2 + int(m)):
                    file.write(str(self.acceptSide[i]))
                    file.write("\n")
                else:
                    file.write(str(self.acceptSide[i]))
                    file.write(",")
            file.close()
            self.acceptSide = [self.settings.value("control_number/box_id_" + str(box_id)),
                               self.settings.value("concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) +
                                                                                          "_on_" + QtCore.QDateTime.
                                                                                          currentDateTime().toString(
                                                                                            QtCore.Qt.ISODate))]
