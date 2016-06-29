# PySide import
from PySide import QtGui

from utilities import ConvertToHFX


class Widget(ConvertToHFX, QtGui.QWidget):
    """
    Widget widget
    """

    def __init__(self, label=None, layout=None):
        super(Widget, self).__init__(label=label, layout=layout)
