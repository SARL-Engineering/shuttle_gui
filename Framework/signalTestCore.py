from PyQt5 import QtCore, QtWidgets


class SignalTest(QtCore.QThread):
    def __init__(self, main_window):
        super(SignalTest, self).__init__()

        self.main_window = main_window

        self.main_window.id_list_widget.currentRowChanged.connect(self.on_list_item_changed)
        self.start()

    def run(self):
        while True:
            self.msleep(500)

    def on_list_item_changed(self, id):
        print(id)


