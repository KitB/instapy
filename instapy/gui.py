import sys

from PySide import QtGui

import basic_ui


# TODO: Stop interacting directly with the notifier; add a socket interface and
# communicate over that
class MainWindow(QtGui.QMainWindow, basic_ui.Ui_MainWindow):
    def __init__(self, notifier, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.updateToggle.valueChanged.connect(self.change_update)
        self.updateNow.clicked.connect(self.do_update)
        self.notifier = notifier

    def change_update(self, n):
        if n == 0:  # Manual update
            self.updateNow.setEnabled(True)
            self.notifier.paused = True
        else:  # Automatic update
            self.updateNow.setEnabled(False)
            self.notifier.paused = False

    def do_update(self):
        self.notifier.reloader.update()


def main(args, notifier=None):
    app = QtGui.QApplication(args)
    window = MainWindow(notifier)
    window.show()

    return_code = app.exec_()
    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv)
