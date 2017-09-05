from PyQt5 import QtCore, QtWidgets
import serial
from serial.tools.list_ports import comports

import serialHandler

from Framework.signalTestCore import SignalTest


class BoxHandler(QtCore.QThread):

    start_all_threads = QtCore.pyqtSignal()
    start_all_boxes_signal = QtCore.pyqtSignal()

    def __init__(self, main_window):
        super(BoxHandler, self).__init__()

        self.main_window = main_window

        self.thread_instances = []
        self.list_w = self.main_window.id_list_widget  # type: QtWidgets.QListWidget
        self.should_run = True
        self.start_all_boxes_manager = False
        self.__connect_signals_to_slots()
        self.start()

    def __connect_signals_to_slots(self):
        # pass
        self.main_window.id_list_widget.currentRowChanged.connect(self.on_list_item_changed)
        self.start_all_boxes_signal.connect(self.on_start)
        my_it = sorted(comports())

        ports = []  # type: serial.Serial

        for n, (port, desc, hwid) in enumerate(my_it, 1):
            # print "    desc: {}\n".format(desc)
            # print "    hwid: {}\n".format(hwid)
            ports.append(port)
            # print ports
            # if pid == "2341":
            #    print "this worked"

        for port in ports:
            if port == "COM1" or port == "COM3":
                continue
            self.thread_instances.append(serialHandler.ThreadOne(self.main_window, self, port))
            print("instance")

        self.start_all_threads.emit()
        i = 1
        for box in self.thread_instances:
            while not box.box_id_found_flag:
                pass
            self.list_w.addItem(str(i))
            i = i+1

        self.list_w.setCurrentRow(0)
        self.msleep(10)

    def on_list_item_changed(self):
        pass

    def on_start(self):
        print("on start")

    def starter(self):
        self.start_all_boxes_signal.emit()
        self.start_all_boxes_manager = False

    def on_stop_all_threads_slot(self):
        print("Box handler exiting")
        self.should_run = False
        for thread in self.thread_instances:
            thread.wait()

