# PySide import
from PySide import QtGui, QtCore

from utilities import ConvertToHFX

from Button import Button
from Label import HorizontalDivider


class Dialog(ConvertToHFX, QtGui.QDialog):
    """
    Dialog pop up widget.
    """

    def __init__(self, header=None, message=None):
        """
        :param message:
        """
        # build class
        super(Dialog, self).__init__(label=header, isDialog=True)

        self._buttons = []

        # set window flags.
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def addButton(self, button, function):
        """
        Add to this dialog.
        :param button:
        :param function:
        :return:
        """
        self._buttons.append(Button(button, function))

    def show(self, *args, **kwargs):
        div = HorizontalDivider()
        self.addWidget(div, 0)

        if not self._buttons:
            self._buttons.append(Button('Ok', self.accept))
            self._buttons.append(Button('Cancel', self.reject))

        for button in self._buttons:
            self.addFooter(button)
        return self.exec_()


class Notification(Dialog):
    """
    Meant to be a single pop up dialog for notifying the user.
    """
    def __init__(self, message, header=None):
        super(Notification, self).__init__(header=header)
        self.addWidget(QtGui.QLabel(message))
        self.addButton('Ok', self.accept)
        self.show()


class Decision(Dialog):
    """
    Meant to be a point for the user to answer a question.
    """
    def __init__(self, message, header=None):
        super(Decision, self).__init__(header=header)
        self.addWidget(QtGui.QLabel(message))
        self.addButton('Yes', self.accept)
        self.addButton('No', self.reject)