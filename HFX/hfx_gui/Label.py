from PySide.QtGui import QLabel, QFrame

from utilities import ConvertToHFX


class Label(ConvertToHFX, QLabel):
    """
    Basic text label
    """


def VerticalDivider():
    """
    Creates a vertical divider line.
    :return:
    """
    divider = QFrame()
    divider.setFrameShape(QFrame.VLine)
    divider.setFrameShadow(QFrame.Raised)
    return divider


def HorizontalDivider():
    """
    Creates a horizontal divider line.
    :return:
    """
    divider = QFrame()
    divider.setFrameShape(QFrame.HLine)
    divider.setFrameShadow(QFrame.Raised)
    return divider