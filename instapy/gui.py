import sys
import signal

from PySide import QtGui

import basic_ui


class MainWindow(QtGui.QMainWindow, basic_ui.Ui_MainWindow):
    def __init__(self, handler, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.updateToggle.valueChanged.connect(self.change_update)
        self.updateNow.clicked.connect(self.do_update)
        self.restartNow.clicked.connect(self.do_restart)
        self.pauseGame.clicked.connect(self.do_pause)
        self.handler = handler

    def change_update(self, n):
        if n == 0:  # Manual update
            self.updateNow.setEnabled(True)
            self.handler.paused = True
        else:  # Automatic update
            self.updateNow.setEnabled(False)
            self.handler.paused = False

    def do_update(self):
        self.handler.reloader.update()

    def do_restart(self):
        self.handler.reloader.restart()

    def do_pause(self):
        self.handler.reloader.toggle_pause()


def main(args, handler=None):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(args)
    window = MainWindow(handler)
    window.show()

    return_code = app.exec_()
    sys.exit(return_code)


if __name__ == '__main__':
    main(sys.argv)
