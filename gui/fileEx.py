# Imports the require libraries
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Create the fileManager library and its contents
class filedialog(QWidget):
    def __init__(self, parent=None):
        super(filedialog, self).__init__(parent)
        # set the layout to default
        layout = QVBoxLayout()
        # create the push button with Open Image File label
        self.btn = QPushButton('Open Image File')
        # if the above button clicked getfile module will start
        self.btn.clicked.connect(self.getfile)
        # add the self.btn with is
        # QFileDialog static method push button
        # to the widget
        layout.addWidget(self.btn)
        # create a label name GSoC
        self.le = QLabel('GSoC')
        # add the self.le with is
        # GSoC label to the widget
        layout.addWidget(self.le)
        # create another push button
        # with is Open Text File object
        self.btn1 = QPushButton('Open Text File')
        # create ths signal of getfiles
        # if the button clicked
        self.btn1.clicked.connect(self.getfiles)
        # add it to the add widget module
        layout.addWidget(self.btn1)

        # create the variable of
        # self.contents for text editor
        self.contents = QTextEdit()
        # add the self.contents to the
        # addwidget
        layout.addWidget(self.contents)
        # initilize it to the layout
        self.setLayout(layout)
        # create the title ile Manager for Incf on GSoC
        self.setWindowTitle('File Manager for Incf on GSoC')

    def getfile(self):
        # start the getfile signal
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', 'Image files(*.jpg *.png *.gif)')
        # set the view format of the images
        self.le.setPixmap(QPixmap(fname))
        # set the image viewer to QPixmap

    def getfiles(self):
        # start the getfiles signal
        # with is text signal
        dlg = QFileDialog()
        # create the dlg Qfiledialog
        dlg.setFileMode(QFileDialog.AnyFile)
        # set to reate anyfile
        dlg.setFilter('Text files (*.txt)')
        # initialize it to reade .txt format
        filenames = QStringList()
        # create the variable of filename
        if dlg.exec_():
            # if dlg.exec_() exist
            filenames = dlg.selectedFiles()
            # filenames variable will select the
            # all files
            f = open(filenames[0], 'r')
            # create the variable of f
            # with will open nay given
            # instructions
            with f:
                # contain f
                data = f.read()
                # data will read
                self.contents.setText(data)
                # .txt format

def main():
    # create the main
    app = QApplication(sys.argv)
    # full application save on app variable
    ex = filedialog()
    # file manager save to ex
    ex.show()
    # show the result of no error
    # or typos
    sys.exit(app.exec_())
    # create the quit button 'X'

if __name__ == '__main__':
    # run main()
    main()
