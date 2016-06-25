# PySide import
from PySide import QtGui, QtCore

from utilities import toHFX, Horizontal, launchPrep


class Dialog(QtGui.QDialog):
    """
    Dialog pop up widget.
    """

    Ask = 0
    Notification = 1

    def __init__(self, message=None, dialogType=None):
        """
        :param message:
        :param dialogType:
        """

        launchPrep(self, '')

        # build class
        super(Dialog, self).__init__()

        # convert Class to HFX
        toHFX(self, Horizontal)

        # instance variables
        self._dialogType = dialogType

        # set window flags.
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # declare message
        if message is None:
            self._name = ''
        else:
            self._name = message


    def show(self, *args, **kwargs):
        wrapper = QtGui.QWidget()
        horLayout = QtGui.QHBoxLayout()
        horLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        wrapper.setLayout(horLayout)
        self.addWidget(wrapper)

        if self._dialogType is None:
            pass

        if self._dialogType == self.Ask:
            pass

        return self.exec_()