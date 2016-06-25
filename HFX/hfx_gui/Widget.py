# PySide import
from PySide import QtGui

from utilities import toHFX, launchPrep


class Widget(QtGui.QWidget):
    """
    Widget widget
    """

    def __init__(self, layout=None):

        launchPrep(self, '')

        super(Widget, self).__init__()

        # convert this widget to an hfx widget
        if layout is None:
            toHFX(self)
        else:
            toHFX(self, layout)
