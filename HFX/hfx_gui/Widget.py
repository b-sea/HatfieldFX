# PySide import
from PySide import QtGui, QtCore

from utilities import ConvertToHFX


class Widget(ConvertToHFX, QtGui.QWidget):
    """
    Widget widget
    """

    def __init__(self, label=None, layout=None):
        super(Widget, self).__init__(label=label, layout=layout)


class Overlay(QtGui.QWidget):
    """
    Widget that overlays the top of any widget provided as the parent.

    To use, override paintEvent.
    """

    def __init__(self, parentWidget):
        super(Overlay, self).__init__(parentWidget)
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):
        """
        Must override.
        :param event:
        :return:
        """
        pass
