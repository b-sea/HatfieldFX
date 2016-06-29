# PySide import
from PySide import QtGui

from utilities import ConvertToHFX


class Button(ConvertToHFX, QtGui.QPushButton):
    """
    Base button class.
    """
    def __init__(self, label, function=None, *args, **kwargs):
        """
        Create a basic button
        :param label:
        :param function:
        """
        super(Button, self).__init__(*args, **kwargs)

        # set button text.
        self.setText(label)

        if function:
            self.connectTo(self.clicked, function)
