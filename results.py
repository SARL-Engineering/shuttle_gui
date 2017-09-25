from PyQt5 import QtCore, QtWidgets, QtGui
import os
from settings_core import ShuttleSettings


class BoxResults(QtCore.QObject):

    def __init__(self):
        self.settings = QtCore.QSettings()
        self.csv_array = []
        self.trialNum =[]
        self.acceptSide = []
        self.seekSideSwaps = []
        self.numSideSwaps = []
        self.timeToAccept = []
        self.rejectTime = []
        self.acceptTime = []
        self.shockModeTime = []
        self.shockedTime = []
        self.counter = 0

    def results_init(self, box_id):

        self.trialNum = [self.settings.value("control_number/box_id_" + str(box_id)),
                         self.settings.value("concentrate/box_id_" + str(box_id)), box_id,
                         QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)]
        mypath = ("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)) + "/test")
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        print(self.trialNum)

    def results_to_array(self, results_array, box_id):
        self.counter = self.counter + 1
        self.trialNum.append(results_array[0])
        print(self.trialNum)
        m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        print("n of trials = ", m)
        print(self.counter)
        if int(m) == int(results_array[0]):
            self.trialNum[0] = self.settings.value("control_number/box_id_" + str(box_id))
            self.trialNum[3] = QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)
            self.trialNum[0] = self.settings.value("control_number/box_id_" + str(box_id))
            self.counter = 0
            print("writing string to file: ", self.trialNum)
            file = open("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
                "control_number/box_id_" + str(box_id)) + "/test/test.txt", "a")
            for i in range(0, len(self.trialNum)):
                if i == (len(self.trialNum) - 1):
                    file.write(str(self.trialNum[i]))
                    file.write("\n")
                else:
                    file.write(str(self.trialNum[i]))
                    file.write(",")
            file.close()
            self.trialNum = [self.settings.value("control_number/box_id_" + str(box_id)),
                             self.settings.value("concentrate/box_id_" + str(box_id)), box_id,
                             QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)]
