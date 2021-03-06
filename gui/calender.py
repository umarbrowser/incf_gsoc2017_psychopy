# imports
import sys
from PyQt4 import QtGui, QtCore

# creating the class for the
# calender app
class Calender(QtGui.QWidget):
    def __init__(self):
        super(Calender, self).__init__()
        self.initUI()
    # create the calender on
    # default pyqt api
    def initUI(self):
        cal = QtGui.QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.move(20, 20)
        cal.clicked[QtCore.QDate].connect(self.showDate)

        self.lb1 = QtGui.QLabel(self)
        date = cal.selectedDate()
        self.lb1.setText(date.toString())
        self.lb1.move(20, 200)

        self.setGeometry(100,100,300,300)
        self.setWindowTitle('Calender for Incf on GSoC')
        self.show()
    # create the text contains date if
    # touch and shows it under
    def showDate(self, date):
        self.lb1.setText(date.toString())

# the main and run if no error
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Calender()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()