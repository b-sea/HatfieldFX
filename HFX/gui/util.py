# PySide imports
from PySide import QtGui, QtCore

# python imports
import os
import sys

__all__ = [
    '_launchPrep',
    '_holdApplication',
    '_imgDirectory',
    'palette',
    'dialog_palette',
    'styleSheet',
    '_PySideFindInList',
    'OPEN_APPLICATION',
]


# Build palette
palette = QtGui.QPalette()
palette.setColor(QtGui.QPalette.Window, QtGui.QColor(30, 30, 30))
palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(175, 175, 175))
palette.setColor(QtGui.QPalette.Base, QtGui.QColor(40, 40, 40))
palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(20, 20, 20))
palette.setColor(QtGui.QPalette.Text, QtGui.QColor(175, 175, 175))
palette.setColor(QtGui.QPalette.Button, QtGui.QColor(30, 30, 30))
palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(175, 175, 175))
palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(175, 175, 175))
palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45, 45, 60))
palette.setColor(QtGui.QPalette.Foreground, QtGui.QColor(175, 175, 175))

# Build palette
dialog_palette = QtGui.QPalette()
dialog_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(30, 30, 30, 50))
dialog_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(175, 175, 175))
dialog_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(40, 40, 40, 50))
dialog_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(20, 20, 20, 50))
dialog_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(175, 175, 175))
dialog_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(30, 30, 30, 50))
dialog_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(175, 175, 175))
dialog_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(175, 175, 175))
dialog_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45, 45, 45))
dialog_palette.setColor(QtGui.QPalette.Foreground, QtGui.QColor(175, 175, 175))


styleSheet = """
QWidget{
    border-radius: 6px;
    outline: 0;
}
QWidget:edit-focus{
    border: 0px;
}
QWidget:focus{
    border: 0px;
}
QLabel{
    color: #b2b2b2;
}
QAction:flat{
    color: #353763;
}
QAction:hover{
    color: #b2b2b2;
}
QActionGroup:exclusive{
    color: #353763;
}
QToolBox{
    color: #b2b2b2;
    border-radius: 6px;
}
QTextEdit{
    border-radius: 7px;
}
QAbstractItemView
{
    border: 0px;
    outline: 0;
}
QHeaderView{
    color: #b2b2b2;
    background-color: #282828;
    border-radius: 7px;
}
QPushButton
{
    color: #b1b1b1;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    border-radius: 7px;
    padding: 3px;
    font-size: 12px;
    padding-left: 5px;
    padding-right: 5px;
}
QPushButton:pressed
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
}
QComboBox
{
    selection-background-color: #1c1c1c;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
    border-style: solid;
    border: 1px solid #1e1e1e;
    border-radius: 7px;
}

QComboBox QAbstractItemView
{
    border: 2px solid darkgray;
    selection-background-color: #ffaa00;
}
QComboBox::drop-down
{
     subcontrol-origin: padding;
     subcontrol-position: top right;
     width: 15px;

     border-left-width: 0px;
     border-left-color: darkgray;
     border-left-style: solid; /* just a single line */
     border-top-right-radius: 3px; /* same radius as the QComboBox */
     border-bottom-right-radius: 3px;
 }
QDockWidget::title
{
    text-align: center;
    spacing: 3px; /* spacing between items in the tool bar */
    background-color: #242424;
}
QDockWidget::title:hover
{
    text-align: center;
    spacing: 3px; /* spacing between items in the tool bar */
    background-color: #353763;
}
QDockWidget::close-button, QDockWidget::float-button
{
    text-align: center;
    spacing: 1px; /* spacing between items in the tool bar */
}
QDockWidget::close-button:hover, QDockWidget::float-button:hover
{
    background: #242424;
}
QDockWidget::close-button:pressed, QDockWidget::float-button:pressed
{
    padding: 1px -1px -1px 1px;
}
QMainWindow::separator
{
    background-color: #282828;
    color: white;
    padding-left: 4px;
    border: 1px solid #282828;
    spacing: 3px; /* spacing between items in the tool bar */
}
QMainWindow::separator:hover
{
    background-color: #353763;
    color: white;
    padding-left: 4px;
    border: 1px solid #282828;
    spacing: 3px; /* spacing between items in the tool bar */
}
"""


OPEN_APPLICATION = None
IN_APP = True


def launchPoint():
    return OPEN_APPLICATION


def _addLoadFonts():
    """
    Load all fonts from the font directory.
    :return:
    """
    try:
        for font in os.listdir(_fontDirectory()):
            QtGui.QFontDatabase.addApplicationFont(os.path.join(_fontDirectory(), font))
    except:
        pass


def _launchPrep(obj, application):
    global OPEN_APPLICATION

    if OPEN_APPLICATION:
        return

    print 'HFX {Application}: Application name ' + application
    print 'HFX {Application}: Launch point entered through ' + str(obj)
    print '\tHFX {System}: Application can be reached through HFX.launchPoint() or HFX.OPEN_APPLICATION'

    OPEN_APPLICATION = obj

    if QtGui.qApp is None:
        global IN_APP
        IN_APP = False
        print
        print 'HFX: No application gui environment found. Initializing new environment.'
        QtGui.QApplication(sys.argv)
        QtGui.qApp.setPalette(palette)
        QtGui.qApp.setStyle('Plastique')
        QtGui.qApp.setStyleSheet(styleSheet)
        print '\tHFX: Environment instance created.'

        QtGui.qApp.setApplicationName(application)
        QtGui.qApp.setObjectName(application)

    _addLoadFonts()


def _holdApplication(application):
    if OPEN_APPLICATION is application:
        QtGui.QMainWindow.show(application)
        if not IN_APP:
            sys.exit(QtGui.qApp.exec_())
    else:
        QtGui.QMainWindow.show(application)


def _clearOpenApplication(app):
    global OPEN_APPLICATION
    if app is OPEN_APPLICATION:
        OPEN_APPLICATION = None


def _imgDirectory():
    return os.path.join(os.path.dirname(__file__), 'img')


def _fontDirectory():
    return os.path.join(os.path.dirname(__file__), 'fonts')


def _PySideFindInList(item, l):
    for i in xrange(0, len(l)):
        try:
            if item is l[i]:
                return i
        except NotImplementedError, e:
            if item == l[i]:
                return i