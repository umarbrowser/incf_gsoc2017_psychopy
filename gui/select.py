import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class combo(QWidget):
    def __init__(self, parent=None):
        super(combo, self).__init__(parent)

        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.cb.addItem('C')
        self.cb.addItem('C++')
        self.cb.addItems(['Java', 'C#', 'Python'])
        self.cb.currentIndexChanged.connect(self.selectionchange)
        layout.addWidget(self.cb)
        self.setLayout(layout)
        self.setWindowTitle('combo box test GSoC')

    def selectionchange(self,i):
        print 'Items in the list are :'
        for count in range(self.cb.count()):
            print 'Current index',1,'Selection change',self.cb.currentText()

def main():
    app = QApplication(sys.argv)
    ex = combo()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()