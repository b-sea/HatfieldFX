# PySide import
from PySide import QtGui

from utilities import ConvertToHFX, Horizontal


class LineEdit(ConvertToHFX, QtGui.QLineEdit):
    """
    LineEdit widget
    """

    def __init__(self, label=None):
        """
        :param label:
        """
        super(LineEdit, self).__init__(label=label, layout=Horizontal)

        # add the label if there is one passed
        if label is not None:
            self.setName(label)

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
