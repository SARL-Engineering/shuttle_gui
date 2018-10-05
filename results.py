# Authors: Aaron Rito, Corwin Perren
# Date: 10/2/17
# Project: SARL Shuttlebox Behavior System
# Client: Oregon State University, SARL lab

########################################################################################################################
#   !!!!IMPORTANT!!!! This class contains queued connections. Do not instantiate this class more than one time or it   #
#                     break the que. To send results form a Shuttlebox use BoxHandler function "send_data" and emit    #
#                     signal with data argument.                                                                       #
#                                                                                                                      #
#   This class contains the data structure and the file writing methods for the program.                               #
########################################################################################################################
from PyQt5 import QtCore
from settings_core import ShuttleSettings
import os


class BoxResults(QtCore.QObject):
    data_ready_signal = QtCore.pyqtSignal(list)

    def __init__(self, main_window, box_handler):
        super(BoxResults, self).__init__()

        # main refs
        self.main_window = main_window
        self.settings = QtCore.QSettings()
        self.settings_class = ShuttleSettings(main_window)

        # The data dictionary and the arrays to be stored in it.
        self.data_dictionary = {}
        self.acceptSide = []
        self.seekSideSwaps = []
        self.numSideSwaps = []
        self.timeToAccept = []
        self.rejectTime = []
        self.acceptTime = []
        self.shockModeTime = []
        self.shockedTime = []
        self.setting_log = []

        # add the arrays to the dictionary
        for i in range(1, self.settings_class.number_of_boxes):
            self.data_dictionary[i] = [self.acceptSide, self.seekSideSwaps, self.numSideSwaps, self.timeToAccept,
                                       self.rejectTime, self.acceptTime, self.shockModeTime, self.shockedTime]

        # variables
        self.counter = 0
        self.res = []
        self.box_handler = box_handler
        self.file_names = ["0 spot dummy", "/acceptSide.txt", "/seekSideSwaps.txt", "/numSideSwaps.txt",
                           "/timeToAccept.txt", "/rejectTime.txt", "/acceptTime.txt", "/shockModeTime.txt",
                           "/shockedTime.txt"]

        # !!!!WARNING!!!! Do not emit a signal for a queued connection from a multi-threaded class!
        #                 Use BoxHaandler.send_data
        self.box_handler.send_data_signal.connect(self.results_to_array, QtCore.Qt.QueuedConnection)
        self.box_handler.send_data_init_signal.connect(self.results_init, QtCore.Qt.QueuedConnection)
        self.m = 0

    def results_init(self, box_id):
        # fill the arrays with the generation and concentrate data
        for i in range(0, 8):
            self.data_dictionary[box_id][i] = self.fill_arrays(box_id)
        self.make_folders(box_id)

    def fill_arrays(self, box_id):
        temp_array = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value(
            "concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" +
                                                   QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))]
        return temp_array

    # TODO: direct this path to a selected directory

    def make_folders(self, box_id):
        path = ("box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)))
        if not os.path.isdir(path):
            os.makedirs(path)

    def results_to_array(self, results_array, box_id):
        # update the the arrays with the test results as they arrive
        for i in range(1, 8):
            self.data_dictionary[box_id][i].append(results_array[i])
        num_trials = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        print("m = " + str(num_trials) + "res = " + str(results_array[0]))
        if int(num_trials) == int(results_array[0]):
            for i in range(1, 8):
                self.data_dictionary[box_id][i] = self.save_results(box_id, self.data_dictionary[box_id][i],
                                                                    self.file_names[i])
        # make note of the settings used in a log file
        file = open("box_results/settings_log.txt", "a")
        self.setting_log.append(self.settings_class.send_box_configs(box_id))
        self.setting_log.append(self.settings_class.send_settle_lights(box_id))
        self.setting_log.append(self.settings_class.send_trial_lights(box_id))
        self.setting_log.append(self.settings_class.send_start_lights(box_id))
        file.write("Shuttlebox_" + str(box_id) + "_on_" +
                              QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
        file.write(str(self.setting_log) + "\n")
        file.close()
        self.setting_log = []

    def save_results(self, box_id, results_array, file_ending):
        # passing in the array to be saved, and updating the time-stamps and settings
        self.res = results_array
        self.res[0] = self.settings.value("control_number/box_id_" + str(box_id))
        self.res[1] = self.settings.value("concentrate/box_id_" + str(box_id))
        self.res[2] = ("Shuttlebox_" + str(box_id) + "_on_" +
                              QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
        print("writing string to file: ", self.res)

        # Write the data to the files in csv format, each newline is a new test
        file = open("box_results/" + self.settings.value(
            "control_number/box_id_" + str(box_id)) + file_ending, "a")
        num_trials = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))

        # The first three spots in the array are the generation data, the rest is length "m" dep. on number of trials
        for i in range(0, (3 + int(num_trials))):
            if i == (2 + int(num_trials)):
                file.write(str(self.res[i]))
                file.write("\n")
            else:
                file.write(str(self.res[i]))
                file.write(",")
        file.close()

        # clear the temp array and reset the generation data, return an initialized array with no data.
        self.res = []
        self.res = [self.settings.value("control_number/box_id_" + str(box_id)), self.settings.value(
            "concentrate/box_id_" + str(box_id)), ("Shuttlebox_" + str(box_id) + "_on_" + QtCore.QDateTime.
                                                   currentDateTime().toString(QtCore.Qt.ISODate))]
        return self.res




