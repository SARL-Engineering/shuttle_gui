from PyQt5 import QtCore, QtWidgets
import serial
from serial.tools.list_ports import comports

import serialHandler

from Framework.signalTestCore import SignalTest


class BoxHandler(QtCore.QThread):

    start_all_threads = QtCore.pyqtSignal()
    start_all_boxes_signal = QtCore.pyqtSignal()
    abort_all_boxes_signal = QtCore.pyqtSignal()

    def __init__(self, main_window):
        super(BoxHandler, self).__init__()

        self.main_window = main_window

        # Gui Object References
        self.id_list_widget = self.main_window.id_list_widget  # type: QtWidgets.QListWidget

        self.thread_instances = []
        self.list_w = self.main_window.id_list_widget  # type: QtWidgets.QListWidget
        self.should_run = True
        self.start_all_boxes_manager = False
        self.abort_all_boxes_manager = False
        self.__connect_signals_to_slots()

        self.setup_gui_elements()
        self.start()

    def __connect_signals_to_slots(self):
        # pass
        self.main_window.id_list_widget.currentRowChanged.connect(self.on_list_item_changed)
        self.start_all_boxes_signal.connect(self.starter)
        self.abort_all_boxes_signal.connect(self.abort_all)
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
            self.thread_instances.append(serialHandler.SerialThread(self.main_window, self, port))

        self.start_all_threads.emit()

        for box in self.thread_instances:
            while not box.box_id_found_flag:
                pass
            self.list_w.addItem(str(box.box_id))

        self.list_w.setCurrentRow(0)
        self.msleep(10)

    def setup_gui_elements(self):
        self.id_list_widget.setSortingEnabled(True)

    def on_list_item_changed(self):
        pass

    def starter(self):
        print("Box manager start all")
        self.start_all_boxes_signal.emit()
        self.start_all_boxes_manager = False

    def abort_all(self):
        print("Box manager abort all")
        self.abort_all_boxes_signal.emit()
        self.abort_all_boxes_manager = False

    def on_stop_all_threads_slot(self):
        print("Box handler exiting")
        self.should_run = False
        for thread in self.thread_instances:
            thread.wait()

