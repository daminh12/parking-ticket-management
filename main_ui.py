from PyQt5 import QtCore, QtGui, QtWidgets
class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        self.setupUi(MainWindow)

    def _text(self, text, name=None, size=11, bold=False, color=None):
        label = QtWidgets.QLabel(text)
        if name:
            label.setObjectName(name)
        font = QtGui.QFont('Segoe UI', size)
        font.setBold(bold)
        label.setFont(font)
        if color:
            label.setStyleSheet('color: %s; background: transparent;' % color)
        return label