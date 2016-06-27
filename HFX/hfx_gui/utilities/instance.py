# python imports
import os
import sys

# PySide import
from PySide import QtGui

# conversion imports
from PySide_to_HFX import _hfx


# Application var
IN_APP = True
OPEN_APPLICATION = None


__all__ = [
    'hfxStylesheet',
    'launchPrep',
    'waitTillClose',
    'validateWidgetLayout',
    'isHFXWidget'
]


def hfxStylesheet():
    """
    HFX stylesheet
    :return:
    """
    return open(os.path.dirname(__file__) + '/stylesheet.qss').read()


def launchPrep(obj, application):
    global OPEN_APPLICATION

    if OPEN_APPLICATION:
        return

    OPEN_APPLICATION = obj

    if QtGui.qApp is None:
        global IN_APP
        IN_APP = False

        # create application
        QtGui.QApplication(sys.argv)

        # set application style
        QtGui.qApp.setStyleSheet(hfxStylesheet())
        QtGui.qApp.setStyle('windowsvista')

        # name the application
        QtGui.qApp.setApplicationName(application)


def waitTillClose(application, onShowCall=None):
    global IN_APP

    QtGui.QWidget.show(application)
    if onShowCall:
        onShowCall()
    if not IN_APP:
        IN_APP = True
        sys.exit(QtGui.qApp.exec_())


def validateWidgetLayout(widget):
    if isHFXWidget(widget):
        return widget.thisWidget()
    return widget


def isHFXWidget(widget):
    if '_hfx' in dir(widget) or isinstance(widget, _hfx):
        return True
    return False

