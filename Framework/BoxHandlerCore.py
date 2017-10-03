# Authors: Aaron Rito, Corwin Perren
# Date: 10/2/17
# Project: SARL Shuttlebox Behavior System
# Client: Oregon State University, SARL lab

########################################################################################################################
#   This thread creates an individual serial thread for each connected Shuttlebox. It also manages communication between
#   the multi-threaded serial thread and teh other classes. Call a function here to emit a signal to communicate with
#   all boxes at the same time, or send data from a box to be printed. NOTE: The only instance of results class is here.
########################################################################################################################

from PyQt5 import QtCore, QtWidgets
import serial
from serial.tools.list_ports import comports
import serialHandler
import results


class BoxHandler(QtCore.QThread):

    # Signals. If you need to send a signal form a serial thread, do it by calling a function and emitting it here.
    start_all_boxes_signal = QtCore.pyqtSignal()
    abort_all_boxes_signal = QtCore.pyqtSignal()
    send_data_signal = QtCore.pyqtSignal(list, int)
    send_data_init_signal = QtCore.pyqtSignal(int)
    change_font_signal = QtCore.pyqtSignal()
    boxes_ready_signal = QtCore.pyqtSignal()

    def __init__(self, main_window):
        super(BoxHandler, self).__init__()

        # GUI Object References
        self.main_window = main_window
        self.id_list_widget = self.main_window.id_list_widget  # type: QtWidgets.QListWidget

        # this will hold the array of serial handler threads.
        self.thread_instances = []

        # more GUI stuff
        self.list_w = self.main_window.id_list_widget  # type: QtWidgets.QListWidget
        self.__connect_signals_to_slots()
        self.setup_gui_elements()

        # instantiate the results class here and here only.
        self.results = results.BoxResults(self.main_window, self)

        # variables
        self.box_count = 0
        self.should_run = True
        self.start()

    def __connect_signals_to_slots(self):

        # make an iterable an array to sort the COM ports
        my_it = sorted(comports())
        ports = []  # type: serial.Serial

        for n, (port, desc, hwid) in enumerate(my_it, 1):
            # print "    desc: {}\n".format(desc)
            # print "    hwid: {}\n".format(hwid)
            ports.append(port)
            # print ports
            # if pid == "2341":
            #    print "this worked"

        # !!!!IMPORTANT!!!! For every device found, open a new serial thread.
        for port in ports:
            if port == "COM1" or port == "COM3":
                continue
            self.thread_instances.append(serialHandler.SerialThread(self.main_window, self, port))

        # Make sure the COM port has a Shuttlebox connected and add it to the clickable numbered list
        for box in self.thread_instances:
            while not box.box_id_found_flag:
                self.msleep(1)
            self.list_w.addItem(str(box.box_id))
        self.list_w.setCurrentRow(0)
        self.msleep(10)

    def setup_gui_elements(self):
        self.id_list_widget.setSortingEnabled(True)

    def start_all_boxes(self):
        # start all the boxes
        print("Box manager starting all")
        self.start_all_boxes_signal.emit()

    def abort_all(self):
        # abort all boxes
        print("Box manager aborting all")
        self.abort_all_boxes_signal.emit()

    def send_data(self, data, box_id):
        # Send data to the results data dictionary
        print("box manager got: ", data, box_id)
        self.send_data_signal.emit(data, box_id)

    def send_data_init(self, box_id):
        # initialize data dictionary arrays on settings change
        print("box manager init: box " + str(box_id))
        self.send_data_init_signal.emit(box_id)

    def font_signal(self):
        self.change_font_signal.emit()

    def box_counter(self):
        # counts a box when it's reported ready
        self.box_count = self.box_count + 1
        if self.box_count == len(self.thread_instances):
            print("all boxes ready")
            self.boxes_ready_signal.emit()

    def on_stop_all_threads_slot(self):
        print("Box handler exiting")
        self.should_run = False
        for thread in self.thread_instances:
            thread.wait()




