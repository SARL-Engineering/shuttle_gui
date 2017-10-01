from PyQt5 import QtCore, QtWidgets
import serial
from serial.tools.list_ports import comports
import serialHandler
import results


class BoxHandler(QtCore.QThread):

    start_all_threads = QtCore.pyqtSignal()
    start_all_boxes_signal = QtCore.pyqtSignal()
    abort_all_boxes_signal = QtCore.pyqtSignal()
    send_data_signal = QtCore.pyqtSignal(list, int)

    def __init__(self, main_window):
        super(BoxHandler, self).__init__()

        self.main_window = main_window

        # Gui Object References
        self.id_list_widget = self.main_window.id_list_widget  # type: QtWidgets.QListWidget

        self.thread_instances = []
        self.list_w = self.main_window.id_list_widget  # type: QtWidgets.QListWidget
        self.should_run = True
        self.__connect_signals_to_slots()
        self.setup_gui_elements()
        self.start()

    def __connect_signals_to_slots(self):
        # pass
        self.main_window.id_list_widget.currentRowChanged.connect(self.on_list_item_changed)
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
                self.msleep(1)
            self.list_w.addItem(str(box.box_id))

        # connect all boxes ready signal to slot
        # emit signal that boxes are ready

        self.list_w.setCurrentRow(0)
        self.msleep(10)
        self.results = results.BoxResults(self.main_window, self)

    def setup_gui_elements(self):
        self.id_list_widget.setSortingEnabled(True)

    def on_list_item_changed(self):
        pass

    def starter(self):
        print("Box manager starting all")
        self.start_all_boxes_signal.emit()

    def abort_all(self):
        print("Box manager aborting all")
        self.abort_all_boxes_signal.emit()

    def on_stop_all_threads_slot(self):
        print("Box handler exiting")
        self.should_run = False
        for thread in self.thread_instances:
            thread.wait()

    def send_data(self, data, box_id):
        print("box manager got: ", data, box_id)
        self.send_data_signal.emit(data, box_id)


