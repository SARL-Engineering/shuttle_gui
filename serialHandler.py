from PyQt5 import QtCore, QtWidgets
import serial
from Framework.BoxHandlerCore import BoxHandler
from settings_core import ShuttleSettings


class SerialThread(QtCore.QThread):
    change_label_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_window, box_handler, comport_string):
        super(SerialThread, self).__init__()

        self.main_window = main_window
        self.box_handler = box_handler
        self.comport_string = comport_string

        # Gui Object References
        self.id_list_widget = self.main_window.id_list_widget  # type: QtWidgets.QListWidget
        #
        self.in_buffer = ""
        self.should_run = True
        self.n_of_trials_flag = None
        self.settings_flag = False
        self.arduino = serial.Serial(comport_string, 9600, bytesize=8, stopbits=1, timeout=None)

        self.box_id_found_flag = False
        self.box_id = None

        self.box_tab_widget = None  # type: QtWidgets.QTabWidget
        self.show_box_tab_widget_flag = False
        self.tab_widget_w = self.main_window.tab_widget_widget
        self.__connect_signals_to_slots()
        self.settings = QtCore.QSettings()
        self.settings_core = ShuttleSettings(main_window)
        self.start()

    def __connect_signals_to_slots(self):
        self.change_label_signal.connect(self.main_window.label.setText)
        self.main_window.id_list_widget.currentRowChanged.connect(self.on_current_box_id_changed_slot)
        self.main_window.stop_all_threads.connect(self.on_stop_all_threads_slot)
        self.box_handler.start_all_boxes_signal.connect(self.on_start_all_boxes)

    def run(self):
        print("serial thread:")

        while self.should_run:

                if self.arduino.inWaiting():
                    in_byte = self.arduino.read().decode("utf-8")
                    self.in_buffer += in_byte

                    if in_byte == "\n":
                        if "Box ID: " in self.in_buffer:
                            self.box_id_found_flag = True
                            self.box_id = int(self.in_buffer.split(": ")[1])
                            print("Box ID: ", self.box_id)

                        print(self.in_buffer)
                        self.in_buffer = ""
                    if self.in_buffer == "x":
                        print("sending configs")
                        self.send_to_box(self.settings_core.send_box_configs(self.box_id))
                        #self.send_to_box("50,1,600,24,12,12,16,8,95,20,500,50,5")
                        self.send_to_box("4,8,100,150,255,0,255,0,50,75,255,0,255,0,200,225,255,0,255,200,0,1")
                        self.send_to_box("7,3,200,15,12,255,10,255,50,75,0,255,0,255,200,225,0,255,255,200,1,0")
                        self.send_to_box("7,3,200,15,12,255,10,255,50,75,0,255,0,255,200,225,0,255,255,200,1,0")
                        self.in_buffer = ""

                self.msleep(50)

    def send_to_box(self, message):
        self.arduino.write(bytes(str(message), "utf-8"))

    def make_box_tab_widget(self, parent):
        self.box_tab_widget = QtWidgets.QTabWidget(parent)
        ##Status tab
        status_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(status_tab_widget, str(self.box_id))
        #get status from arduino here.....
        #control tab
        self.make_control_tab()
        self.make_settings_tab()

        ##Lights tab
        lights_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(lights_tab_widget, "Lights")

        return self.box_tab_widget

    def make_settings_tab(self):
        settings_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(settings_tab_widget, "Settings")
        #make the boxes
        self.n_of_trials_box = QtWidgets.QSpinBox()
        #set the ranges
        self.n_of_trials_box.setRange(0, 255)
        #add the elements to the layout
        settings_layout = QtWidgets.QFormLayout()
        settings_tab_widget.setLayout(settings_layout)
        settings_layout.addRow("Number of Trials", self.n_of_trials_box)
        self.n_of_trials_box.valueChanged.connect(self.n_of_trials_slot)
        print("this runs")
        #retrive the settings
        self.n_of_trials_box.setValue(self.settings.value(("boxes/box_id_" + str(self.box_id) + "/n_of_trials"), int))
        #connect the slots
        print("settings tab made")

    def n_of_trials_slot(self):
        print("test " + str(self.box_id))
        self.settings.setValue(("boxes/box_id_" + str(self.box_id) + "/n_of_trials"), self.n_of_trials_box.value())

    def make_control_tab(self):
        ##Setting the layout
        control_tab_widget = QtWidgets.QWidget()
        self.box_tab_widget.addTab(control_tab_widget, "Control")
        control_tab_layout = QtWidgets.QVBoxLayout()
        control_tab_widget.setLayout(control_tab_layout)
        control_tab_layout.setSizeConstraint(3)
        ##Creating the button instances
        control_start_button = QtWidgets.QPushButton("Start")
        control_start_all_button = QtWidgets.QPushButton("Start All")
        control_start_group_button = QtWidgets.QPushButton("Start Group")
        control_abort_button = QtWidgets.QPushButton("Abort")
        ##Adding the buttons to the layout
        control_tab_layout.addWidget(control_start_button)
        control_tab_layout.addWidget(control_start_all_button)
        control_tab_layout.addWidget(control_start_group_button)
        control_tab_layout.addWidget(control_abort_button)
        ##slots
        control_start_button.clicked.connect(self.button_one_slot)
        control_start_all_button.clicked.connect(self.button_two_slot)
        control_start_group_button.clicked.connect(self.button_three_slot)
        control_abort_button.clicked.connect(self.button_four_slot)

    def start_all_boxes_slot(self):
        self.start_all_boxes_signal.emit()

    def button_one_slot(self):
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("251")
        print("Start pushed")
        self.msleep(50)

    def button_two_slot(self):
        BoxHandler.start_all_boxes_manager = True
        BoxHandler.starter(self.box_handler)
        print("Start all signal pushed")

    def button_three_slot(self):
        print("button three" + str(self.box_id))

    def button_four_slot(self):
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("253")
        print("Abort pushed")
        self.msleep(50)

    def on_start_all_boxes(self):
        self.send_to_box(self.box_id)
        self.send_to_box(",")
        self.send_to_box("252")
        self.msleep(50)

    def on_settings_clicked_slot(self):
        self.settings_flag = True

    def on_current_box_id_changed_slot(self, row_id):
        self.settings.sync()
        list_box_id = int(self.id_list_widget.currentItem().text())
        # list_box_id = row_id + 1
        if list_box_id == self.box_id:
            layout = self.tab_widget_w.layout()  # type: QtWidgets.QLayout

            for i in reversed(range(layout.count())):
                widgetToRemove = layout.itemAt(i).widget()
                # remove it from the layout list
                layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

            layout.addWidget(self.make_box_tab_widget(self.tab_widget_w))
            self.id_list_widget.sortItems()

    def on_stop_all_threads_slot(self):
        self.should_run = False
