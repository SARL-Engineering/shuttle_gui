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
        self.res = []

    def results_init(self, box_id):

        #initialize the arrays, used for clearing old data as well
        self.acceptSide = self.fill_arrays(box_id)
        self.seekSideSwaps = self.fill_arrays(box_id)
        self.numSideSwaps = self.fill_arrays(box_id)
        self.timeToAccept = self.fill_arrays(box_id)
        self.rejectTime = self.fill_arrays(box_id)
        self.acceptTime = self.fill_arrays(box_id)
        self.shockModeTime = self.fill_arrays(box_id)
        self.shockedTime = self.fill_arrays(box_id)

        #make the file paths if the do not exist already
        self.make_folders(box_id, "/acceptSide")
        self.make_folders(box_id, "/seekSideSwaps")
        self.make_folders(box_id, "/numSideSwaps")
        self.make_folders(box_id, "/timeToAccept")
        self.make_folders(box_id, "/rejectTime")
        self.make_folders(box_id, "/acceptTime")
        self.make_folders(box_id, "/shockModeTime")
        self.make_folders(box_id, "/shockedTime")

    def fill_arrays(self, box_id):
        temp = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value("concentrate/box_id_" +
                                                                                                 str(box_id)), (
            "Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))]
        return temp

    def make_folders(self, box_id, file_ending):
        path = ("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)) + file_ending)
        if not os.path.isdir(path):
            os.makedirs(path)

    def results_to_array(self, results_array, box_id):
        self.acceptSide.append(results_array[0])
        print(self.acceptSide)
        m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        print("n of trials = ", m)
        if int(m) == int(results_array[0]):
            self.save_results(box_id, self.acceptSide, "/acceptSide/acceptSide.txt")
            self.acceptSide = self.update_results_array()
            print(self.acceptSide)

    def save_results(self, box_id, results_array, file_ending):
        self.res = results_array
        self.res[0] = self.settings.value("control_number/box_id_" + str(box_id))
        self.res[1] = self.settings.value("concentrate/box_id_" + str(box_id))
        self.res[2] = ("Shuttlebox_" + str(box_id) + "_on_" +
                              QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
        print("writing string to file: ", self.res)
        file = open("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)) + file_ending, "a")
        m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        for i in range(0, (3 + int(m))):
            if i == (2 + int(m)):
                file.write(str(self.res[i]))
                file.write("\n")
            else:
                file.write(str(self.res[i]))
                file.write(",")
        file.close()
        self.res = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value(
            "concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.
                                                   currentDateTime().toString(QtCore.Qt.ISODate))]

    def update_results_array(self):
        return self.res
