# PySide import
from PySide import QtGui

from utilities import ConvertToHFX, PythonHighlighter, JSONHighlighter, XMLHighlighter


__all__ = [
    'MultiLineEdit'
]


class MultiLineEdit(ConvertToHFX, QtGui.QTextEdit):
    """
    MultiLineEdit widget
    """

    Python = PythonHighlighter
    JSON = JSONHighlighter
    XML = XMLHighlighter

    def __init__(self, label=None, syntax=None):
        """
        :param label:
        """
        super(MultiLineEdit, self).__init__(label=label)

        char_format = QtGui.QTextCharFormat()
        char_format.setFont(self.font())

        if syntax:
            syntax(self.document())

