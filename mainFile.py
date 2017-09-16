import sys
from PyQt5 import QtCore, QtWidgets, uic
import signal
import serial
from serial.tools.list_ports import comports
import serialHandler
from Framework.BoxHandlerCore import BoxHandler
from settings import ShuttleSettings

UI_FILE_PATH = "arduinoform_corwin.ui"


class NewWindow(QtWidgets.QMainWindow):
    stop_all_threads = QtCore.pyqtSignal()  # signal from class QmainWindow to stop

    def __init__(self, parent=None):
        super(NewWindow, self).__init__(parent)
        uic.loadUi(UI_FILE_PATH, self)

        self.settings_class = ShuttleSettings(self)
        self.box_handler_class = BoxHandler(self)

    def closeEvent(self, event):
        self.stop_all_threads.emit()

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)

    myWindow = NewWindow()

    myWindow.show()

    app.exec_()

