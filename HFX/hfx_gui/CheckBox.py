# PySide import
from PySide import QtGui

from utilities import ConvertToHFX


class CheckBox(ConvertToHFX, QtGui.QCheckBox):
    """
    Base check box class.
    """
    def __init__(self, label, *args, **kwargs):
        """
        Create a basic check box.
        :param label:
        """
        super(CheckBox, self).__init__(*args, **kwargs)

        self.setText(label)

    def setValue(self, value):
        """
        Set the value
        :param value:
        :return:
        """
        self.setChecked(value)

    def value(self):
        """
        Get the value
        :return:
        """
        return self.isChecked()