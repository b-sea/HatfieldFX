# PySide import
from PySide import QtGui

from utilities import ConvertToHFX, Horizontal


class OptionBox(ConvertToHFX, QtGui.QComboBox):
    """
    OptionBox widget
    """

    def __init__(self, label=None):
        """
        :param label:
        """
        super(OptionBox, self).__init__(label=label, layout=Horizontal)

    def value(self):
        """
        Just a wrapper for current text.
        :return:
        """
        return str(self.currentText())
