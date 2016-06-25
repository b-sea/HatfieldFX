# PySide import
from PySide import QtGui

from utilities import toHFX, Horizontal, launchPrep


class OptionBox(QtGui.QComboBox):
    """
    OptionBox widget
    """

    def __init__(self, label=None):
        """
        :param label:
        """

        launchPrep(self, '')

        super(OptionBox, self).__init__()

        # convert this widget to an hfx widget
        toHFX(self, Horizontal)

        # add the label if there is one passed
        if label is not None:
            labelWidget = QtGui.QLabel(self)
            labelWidget.setText(label)
            self.addWidget(labelWidget, 0)

    def value(self):
        """
        Just a wrapper for current text.
        :return:
        """
        return str(self.currentText())
