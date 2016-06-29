# PySide import
from PySide import QtGui, QtCore

from utilities import ConvertToHFX, Horizontal
from Button import Button


class LineEdit(ConvertToHFX, QtGui.QLineEdit):
    """
    LineEdit widget
    """

    def __init__(self, label=None):
        """
        :param label:
        """
        super(LineEdit, self).__init__(label=label, layout=Horizontal)

    def addCompleterItems(self, items):
        """
        Add a list of words as a completer.
        :return:
        """
        completer = QtGui.QCompleter(items, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)

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


class FileLineEdit(LineEdit):
    """
    Create a File browser LineEdit
    """
    def __init__(self, label):
        super(FileLineEdit, self).__init__(label)

        self.setMinimumWidth(200)

        # add browse button
        self.addWidget(Button('Browse', self.browse))

        # set up completer
        completer = QtGui.QCompleter(self)
        completer.setModel(QtGui.QDirModel(completer))
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)

    def browse(self):
        """
        Launch browser to find a path.
        :return:
        """
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        dialog.exec_()
        self.setValue(dialog.selectedFiles()[0])
