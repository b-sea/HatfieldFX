# PySide import
from PySide import QtGui

from utilities import toHFX, Horizontal, launchPrep


class LineEdit(QtGui.QLineEdit):
    """
    LineEdit widget
    """

    def __init__(self, label=None):
        """
        :param label:
        """

        launchPrep(self, '')

        super(LineEdit, self).__init__()

        # convert this widget to an hfx widget
        toHFX(self, Horizontal)

        # add the label if there is one passed
        if label is not None:
            labelWidget = QtGui.QLabel(self)
            labelWidget.setText(label)
            self.addWidget(labelWidget, 0)

    def setValue(self, value):
        """
        Set the value of this line edit
        :param value:
        :return:
        """
        self.setText(value)

    def value(self):
        """
        Return the value of this line edit
        :return:
        """
        return str(self.text())
