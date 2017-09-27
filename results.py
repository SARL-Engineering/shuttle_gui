from PyQt5 import QtCore
import os


class BoxResults(QtCore.QObject):

    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = QtCore.QSettings()
        self.acceptSide = []
        self.seekSideSwaps = []
        self.numSideSwaps = []
        self.timeToAccept = []
        self.rejectTime = []
        self.acceptTime = []
        self.shockModeTime = []
        self.shockedTime = []
        self.counter = 0
        self.res = []

    def results_init(self, box_id):
        ####initialize the arrays, used for clearing old data as well####
        self.acceptSide = self.fill_arrays(box_id)
        self.seekSideSwaps = self.fill_arrays(box_id)
        self.numSideSwaps = self.fill_arrays(box_id)
        self.timeToAccept = self.fill_arrays(box_id)
        self.rejectTime = self.fill_arrays(box_id)
        self.acceptTime = self.fill_arrays(box_id)
        self.shockModeTime = self.fill_arrays(box_id)
        self.shockedTime = self.fill_arrays(box_id)
        ####make the file paths if the do not exist already####
        self.make_folders(box_id)

    def fill_arrays(self, box_id):
        temp_array = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value("concentrate/box_id_" +
                                                                                                 str(box_id)), (
            "Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))]
        return temp_array

    def make_folders(self, box_id):
        path = ("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)))
        if not os.path.isdir(path):
            os.makedirs(path)

    def results_to_array(self, results_array, box_id):
        ####update the the arrays with the test results as they arrive####
        self.acceptSide.append(results_array[1])
        self.seekSideSwaps.append(results_array[2])
        self.numSideSwaps.append(results_array[3])
        self.timeToAccept.append(results_array[4])
        self.rejectTime.append(results_array[5])
        self.acceptTime.append(results_array[6])
        self.shockModeTime.append(results_array[7])
        self.shockedTime.append(results_array[8])
        m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        print("m = " + str(m) + "res = " + str(results_array[0]))
        if int(m) == int(results_array[0]):
            #####If the test is over print the results to the files and clear the arrays for new data####
            self.save_results(box_id, self.acceptSide, "/acceptSide.txt")
            self.acceptSide = self.update_results_array()
            self.save_results(box_id, self.seekSideSwaps, "/seekSideSwaps.txt")
            self.seekSideSwaps = self.update_results_array()
            self.save_results(box_id, self.numSideSwaps, "/numSideSwaps.txt")
            self.numSideSwaps = self.update_results_array()
            self.save_results(box_id, self.timeToAccept, "/timeToAccept.txt")
            self.timeToAccept = self.update_results_array()
            self.save_results(box_id, self.rejectTime, "/rejectTime.txt")
            self.rejectTime = self.update_results_array()
            self.save_results(box_id, self.acceptTime, "/acceptTime.txt")
            self.acceptTime = self.update_results_array()
            self.save_results(box_id, self.shockModeTime, "/shockModeTime.txt")
            self.shockModeTime = self.update_results_array()
            self.save_results(box_id, self.shockedTime, "/shockedTime.txt")
            self.shockedTime = self.update_results_array()

    def save_results(self, box_id, results_array, file_ending):
        ####passing in the array to be saved, and updating the timestamps and settings####
        self.res = results_array
        self.res[0] = self.settings.value("control_number/box_id_" + str(box_id))
        self.res[1] = self.settings.value("concentrate/box_id_" + str(box_id))
        self.res[2] = ("Shuttlebox_" + str(box_id) + "_on_" +
                              QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
        print("writing string to file: ", self.res)
        ####Write the data to the files in csv format, each newline is a new test####
        file = open("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)) + file_ending, "a")
        m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        ####The first three spots in the array are the generation data, the rest is length "m" dep. on number of trials#
        for i in range(0, (3 + int(m))):
            if i == (2 + int(m)):
                file.write(str(self.res[i]))
                file.write("\n")
            else:
                file.write(str(self.res[i]))
                file.write(",")
        file.close()
        ####clear the temp file and reset the generation data
        self.res = []
        self.res = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value(
            "concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.
                                                   currentDateTime().toString(QtCore.Qt.ISODate))]

    def update_results_array(self):
        ####update a specific array with the generation data#####
        return self.res
