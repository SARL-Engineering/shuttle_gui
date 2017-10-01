from PyQt5 import QtCore, QtGui, QtWidgets
from results import BoxResults
import os


class DataWrite(QtCore.QObject):

    def __init__(self, main_window):

        self.main_window = main_window
        BoxResults.data_ready_signal.connect(self.write_data())

    def write_data(self, data_to_write):

        print("The argument is: " + data_to_write)
        # ####Write the data to the files in csv format, each newline is a new test####
        # file = open("C:/Users/AaronR/PycharmProjects/shuttle_gui/box_results/" + self.settings.value(
        #     "control_number/box_id_" + str(box_id)) + file_ending, "a")
        # m = self.settings.value(("boxes/box_id_" + str(box_id) + "/n_of_trials"))
        # ####The first three spots in the array are the generation data, the rest is length "m" dep. on number of trials#
        # for i in range(0, (3 + int(m))):
        #     if i == (2 + int(m)):
        #         file.write(str(self.res[i]))
        #         file.write("\n")
        #     else:
        #         file.write(str(self.res[i]))
        #         file.write(",")
        # file.close()


