import sys
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

    def __init__(self, parent=None):
        super(NewWindow, self).__init__(parent)
        uic.loadUi(UI_FILE_PATH, self)

        self.welcome = QtWidgets.QDialog()

        self.welcome.setWindowTitle("SARL Shuttlebox Behavior System")
        self.welcome_label = QtWidgets.QLabel(
            "Welcome to the SARL Shuttlebox Behavior System. Brought to you by: \n Aaron Rito," +
            "Corwin Perren, Vance Langer. Press GO! to get started.")
        self.welcome_button = QtWidgets.QPushButton("GO!")
        self.welcome_window = QtWidgets.QGraphicsScene()
        self.welcome_image = QtGui.QImage("logo.png")
        self.lab = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout()
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.welcome_image))
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.welcome_label)
        layout.addWidget(self.welcome_button)
        self.welcome_button.clicked.connect(self.welcome_slot)

        self.welcome.setLayout(layout)
        self.welcome.resize(300, 300)
        self.welcome.show()

        self.settings_class = ShuttleSettings(self)
        self.box_handler_class = BoxHandler(self)
        self.results = BoxResults(self, self.box_handler_class)
        self.welcome.exec()

    def welcome_slot(self):
        self.welcome.accept()

    def closeEvent(self, event):
        self.stop_all_threads.emit()

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)

    myWindow = NewWindow()

    myWindow.show()

    app.exec_()

