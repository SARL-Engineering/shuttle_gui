import sys
import time as systime
import signal
from PyQt5 import QtCore, QtWidgets, QtGui, uic
import serialHandler #even though this isnt used, it needs to be here for the program to compile?
from Framework.BoxHandlerCore import BoxHandler
from settings_core import ShuttleSettings
from results import BoxResults
from dataWriter import DataWrite

UI_FILE_PATH = "arduinoform_corwin.ui"


class NewWindow(QtWidgets.QMainWindow):
    stop_all_threads = QtCore.pyqtSignal()  # signal from class QmainWindow to stop
    welcome_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(NewWindow, self).__init__(parent)
        uic.loadUi(UI_FILE_PATH, self)

        self.welcome_signal.connect(self.welcome_open)
        self.welcome = QtWidgets.QProgressDialog(parent)
        self.welcome.setCancelButton(None)
        self.welcome.setRange(0, 0)
        self.my_font = QtGui.QFont()
        self.my_font.setPointSizeF(11)
        self.my_font.setBold(True)
        self.welcome.setFont(self.my_font)
        self.welcome.setWindowTitle("SARL Shuttlebox Behavior System")
        self.welcome_label = QtWidgets.QLabel(
            "Welcome to the SARL Shuttlebox Behavior System. Concept by: Aaron Rito," +
            " Corwin Perren, and Vance Langer.")
        self.welcome_button = QtWidgets.QPushButton(None)
        self.welcome_window = QtWidgets.QGraphicsScene()
        self.welcome_image = QtGui.QImage("big_logo.png")
        self.lab = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout()
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.welcome_image))
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.welcome_label)
        layout.addSpacing(30)
        #layout.addWidget(self.welcome_button)
        #self.welcome_button.clicked.connect(self.welcome_slot)

        self.welcome.setLayout(layout)
        self.welcome.resize(850, 500)
        self.welcome.setModal(True)
        self.welcome.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.should_run = True
        self.run()

    def run(self):

        if self.should_run:
            self.settings_class = ShuttleSettings(self)
            self.box_handler_class = BoxHandler(self)
            self.box_handler_class.change_font_signal.connect(self.change_font)
            self.box_handler_class.boxes_ready_signal.connect(self.welcome_slot)
            self.welcome_signal.emit()
            self.should_run = False

    def welcome_open(self):
        self.welcome.exec()

    def welcome_slot(self):
        print("welcome slot")
        self.welcome.done(0)

    def closeEvent(self, event):
        self.stop_all_threads.emit()

    def change_font(self):
        font, valid = QtWidgets.QFontDialog.getFont()
        if valid:
            self.styleChoice.setFont(font)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)

    myWindow = NewWindow()

    myWindow.show()

    app.exec_()

