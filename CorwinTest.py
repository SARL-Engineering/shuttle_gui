class PrintStuff:
    def __init__(self, COM):
        self.my_COM = COM

    def print_my_com(self):
        print self.my_COM


class NewPrintStuff(QtWidgets.QTabWidget):
    def __init__(self):
        self.print_my_com()
        pass

if __name__ == '__main__':
    my_classes = {}

    for x in range(10):
        my_classes['ID:'+str(x)] = PrintStuff("COM" + str(x))

    for x in my_classes:
        print x
        my_classes[x].print_my_com()

   # my_dict = {'1': 1, '2':2}

 #   print my_dict['2']