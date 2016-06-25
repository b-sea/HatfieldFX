# gui util import
import util

# PySide import
from PySide import QtGui, QtCore

# Python imports
import os

__all__ = [
    'Application',
    'Widget',
    'Control',
    'Dialog',
    'Notification'
]


class Application(QtGui.QMainWindow):
    """
    Main application gui interface.
    """

    # dock variables
    DockLeft = QtCore.Qt.LeftDockWidgetArea
    DockRight = QtCore.Qt.RightDockWidgetArea
    DockBottom = QtCore.Qt.BottomDockWidgetArea
    DockTop = QtCore.Qt.TopDockWidgetArea

    def __init__(self, applicationName, icon=None, searchBar=None):
        """
        :param applicationName: 
        :param icon: 
        :return: 
        """
        util._launchPrep(self, applicationName)

        super(Application, self).__init__()

        self.setPalette(util.palette)
        self.setStyleSheet(util.styleSheet)
        self._menuBarMap = {}
        self.searchBar = None

        # Set object information
        self.setObjectName(applicationName)

        # Set window information
        self.setWindowTitle(applicationName)

        if icon is None:
            self.setWindowIcon(QtGui.QIcon(os.path.join(util._imgDirectory(), 'hfx.png')))
            QtGui.qApp.setWindowIcon(QtGui.QIcon(os.path.join(util._imgDirectory(), 'hfx.png')))
        else:
            self.setWindowIcon(QtGui.QIcon(icon))
            QtGui.qApp.setWindowIcon(QtGui.QIcon(icon))

        if searchBar:
            status = QtGui.QStatusBar(self)
            self.searchBar = QtGui.QLineEdit(self)
            self.searchBar.setPlaceholderText('Global search...')
            self.searchBar.setMaximumWidth(200)
            self.searchBar.setStyleSheet(util.styleSheet)
            status.addWidget(self.searchBar)
            self.setStatusBar(status)
            self.searchBar.textChanged.connect(self.globalSearch)


    def closeEvent(self, event):
        util._clearOpenApplication(self)
        QtGui.QMainWindow.close(self)

    def name(self):
        return self.objectName()

    def globalSearch(self, keyword=None):
        """
        Search globally through all widgets.
        :return:
        """
        if not keyword:
            keyword = self.searchBar.text()

        for w in Widget.INSTANCES:
            w.search(keyword)

    def addFunction(self, menu, name, function=None, tip=None):
        if menu not in self._menuBarMap:
            self._menuBarMap[menu] = self.menuBar().addMenu(menu)

        if function is None or name == '':
            self._menuBarMap[menu].addSeparator()
            return

        action = self._menuBarMap[menu].addAction(name)
        if tip:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        else:
            action.setToolTip(function.__doc__)
            action.setStatusTip(function.__doc__)
        action.triggered.connect(function)

    def setMainWidget(self, widget):
        """
        Set the main widget for the application. It can also be a control but should be a widget wrapper.
        :param widget:
        :return:
        """
        widget.setPalette(util.palette)
        self.setCentralWidget(widget)

    def addPanel(self, control, locaction):
        """
        Add a control or widget to this Application as a panel.
        :param control:
        :return:
        """
        control.setPalette(util.palette)
        dock = QtGui.QDockWidget(control.name())
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        dock.setWidget(control)
        dock.setPalette(util.palette)
        self.addDockWidget(locaction, dock)

    def show(self):
        util._holdApplication(self)


class Widget(QtGui.QWidget):
    """
    Base widget class
    """

    INSTANCES = []

    def __init__(self, name=None, vertical=True, width=None, height=None, searchable=None):
        """
        :param width:
        :param height:
        :return:
        """
        super(Widget, self).__init__()
        self.INSTANCES.append(self)

        self.bar = None
        self.customContextMenu = None
        self.customFunctions = {}
        self.widgetMenu = None
        self.setStyleSheet(util.styleSheet)
        self._searchBar = None

        if name is None:
            self._name = ''
        else:
            self._name = name
        if width is not None:
            self.setMinimumWidth(width)

        if height is not None:
            self.setMinimumHeight(height)

        if vertical:
            self._layout = QtGui.QVBoxLayout()
        else:
            self._layout = QtGui.QHBoxLayout()

        self._layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        vertLayoutWrapper = QtGui.QVBoxLayout()

        if name != '' or name is not None:
            label = QtGui.QLabel(name)
            f = QtGui.QFont()
            f.setFamily('Overseer')
            f.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1.2)
            f.setItalic(True)
            f.setPointSize(18)
            label.setFont(f)
            vertLayoutWrapper.addWidget(label)

        vertLayoutWrapper.addLayout(self._layout)
        vertLayoutWrapper.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self._vert = vertLayoutWrapper
        self.setLayout(vertLayoutWrapper)

        if searchable:
            self._searchBar = QtGui.QLineEdit()
            self._searchBar.setPlaceholderText('Search...')
            self._searchBar.setMaximumWidth(300)
            self.addFunction('Search', self._searchBar)

            self._searchBar.textChanged.connect(self.search)

    def setKeywords(self, keywordList):
        """
        Add a list of keywords to the search bar
        :param keywordList:
        :return:
        """
        if self._searchBar:
            self._searchBar.setCompleter(QtGui.QCompleter(keywordList))

    def searchWord(self):
        """
        Get the current search bar value
        :return:
        """
        if self._searchBar is None:
            return
        return self._searchBar.text()

    def search(self, word=None):
        """
        :return:
        """
        pass

    def name(self):
        """
        Name of this Widget.
        :return:
        """
        return self._name

    def contextMenuEvent(self, event):
        if self.customContextMenu:
            funcBar = QtGui.QComboBox(self)
            funcBar.addItems(self.customFunctions.keys())
            self.customContextMenu.exec_(self.mapToGlobal(event.pos()))
        else:
            QtGui.QWidget.contextMenuEvent(self, event)

    def addControl(self, control):
        """
        Add a control (or widget) to this Widget
        :param control:
        :return:
        """
        control.setPalette(util.palette)
        self._layout.addWidget(control)

    def removeControl(self, control):
        """
        Remove a control (or widget) from this Widget
        :param control:
        :return:
        """
        self._layout.removeWidget(control)

    def addFunction(self, functionName=None, func=None, tip=None, contextMenu=False):
        """
        Add a function to the function menu.
        :param functionName:
        :param func:
        :return:
        """

        if contextMenu:
            if not self.customContextMenu:
                self.customContextMenu = QtGui.QMenu(self)
                self.customContextMenu.setPalette(util.palette)
                self.customContextMenu.addSeparator()

            if isinstance(func, QtGui.QWidget):
                if self.widgetMenu is None:
                    self.widgetMenu = Widget()
                    layout = QtGui.QVBoxLayout()
                    menu = self.customContextMenu.addMenu('Widgets')
                    menu.setLayout(layout)
                    menu.setPalette(util.palette)
                    layout.addWidget(self.widgetMenu)
                self.widgetMenu.addControl(func)
            else:
                if functionName == '' or functionName is None:
                    self.customContextMenu.addSeparator()
                    return
                action = self.customContextMenu.addAction(functionName)
                action.triggered.connect(func)

                self.customFunctions[functionName] = func

                if tip:
                    action.setToolTip(tip)
                    action.setStatusTip(tip)
                else:
                    action.setToolTip(func.__doc__)

            return

        if self.bar is None:
            self.bar = QtGui.QToolBar()
            self._vert.insertWidget(1, self.bar)

        if isinstance(func, QtGui.QWidget):
            self.bar.addWidget(func)
        else:
            action = self.bar.addAction(functionName)
            action.triggered.connect(func)
            if tip:
                action.setToolTip(tip)
                action.setStatusTip(tip)
            else:
                action.setToolTip(func.__doc__)
                action.setStatusTip(func.__doc__)


class Control(QtGui.QWidget):
    """
    Base control class
    """

    # instance refresher.

    INSTANCES = []

    def __init__(self, name, label=None, canToggle=False, width=None, height=None, tooltip=None, inLineLabel=False):
        """
        :param label:
        :return:
        """
        super(Control, self).__init__()

        Control.INSTANCES.append(self)

        self._toolBar = QtGui.QToolBar()
        self._funcBar = QtGui.QToolBar()
        self._name = name
        self._subWidgets = []
        self._subLayout = QtGui.QVBoxLayout()
        top = QtGui.QVBoxLayout()
        self.setStyleSheet(util.styleSheet)

        self._nestedControls = []

        if width is not None:
            self.setMinimumWidth(width)
        if height is not None:
            self.setMinimumHeight(height)

        # Toggle
        if canToggle:
            self._controlToggle = self._toolBar.addAction('O')
            self._controlToggle.setCheckable(True)
            self._controlToggle.setChecked(True)
            self._toolBar.addSeparator()

        self._funcBar.addSeparator()
        self.f = self._funcBar.addAction('')
        self._subControlsMenu = QtGui.QMenu()
        self._subControlsMenu.setPalette(util.palette)
        self._subControlsMenu.setLayout(self._subLayout)
        self.f.setMenu(self._subControlsMenu)
        self.f.setToolTip('Functions and sub-widgets')
        self._funcBar.setVisible(False)

        self._subControlAction = QtGui.QLabel(label)
        self._subControlAction.setPalette(util.palette)
        if not self._subControlAction.text().endswith(':') and inLineLabel:
            self._subControlAction.setText(self._subControlAction.text() + ': ')
        if tooltip is None:
            tooltip = 'HFX Control instance. ' \
                      '\nPlease modify this in your code using the keyword "tooltip" in the constructor.'

        self._subControlAction.setToolTip(tooltip)

        if label is None or label == '':
            self._subControlAction.setMaximumWidth(20)
            self._subControlAction.setHidden(True)
        else:
            if inLineLabel:
                self._toolBar.addWidget(self._subControlAction)
            else:
                top.addWidget(self._subControlAction)

        side = QtGui.QHBoxLayout()
        side.addWidget(self._toolBar)
        side.addWidget(self._funcBar)
        top.addLayout(side)
        self.setLayout(top)

    @classmethod
    def _refreshCallback(cls):
        for instance in cls.INSTANCES:
            instance.refresh()

    def refresh(self):
        """
        Refresh callback.
        :return:
        """
        pass

    def name(self):
        """
        Name of this Control.
        :return:
        """
        return self._name

    def getControl(self, name):
        """
        Get a control nested in this control by name.
        :param name:
        :return:
        """
        for control in self._nestedControls:
            if name == control.name():
                return control

    def addControl(self, control, toolBar=True):
        """
        Add a control (or widget) to this control
        :param control:
        :return:
        """
        control.setPalette(util.palette)
        if toolBar:
            self._toolBar.addWidget(control)
        else:
            self.layout().addWidget(control)

        if isinstance(control, Control):
            self._nestedControls.append(control)

    def removeControl(self, control):
        """
        Remove a control (or widget) from this control
        :param control:
        :return:
        """
        self._toolBar.removeWidget(control)
        self._nestedControls.pop(self._nestedControls.index(control))

    def addFunction(self, functionName, func, *args, **kwargs):
        """
        Add a function to the function menu.
        :param functionName:
        :param func:
        :return:
        """
        self._funcBar.setVisible(True)

        action = self._subControlsMenu.addAction(functionName)

        if 'partial' in kwargs:
            if kwargs['partial'] is not None:
                def f():
                    return func(*args)
                action.triggered.connect(f)
                return
        else:
            action.triggered.connect(func)

    def clearSubControls(self):
        """
        Remove all sub controls from the
        :return:
        """
        for sub in self._subWidgets:
            self._subLayout.removeWidget(sub)
        self._funcBar.setVisible(False)

        self._subLayout = QtGui.QVBoxLayout()
        self._subControlsMenu = QtGui.QMenu()
        self._subControlsMenu.setPalette(util.palette)
        self._subControlsMenu.setLayout(self._subLayout)
        self.f.setMenu(self._subControlsMenu)

        self._subWidgets = []

    def addSubControl(self, control):
        """
        Add a control to the submenu controls section
        :param control:
        :return:
        """
        self._funcBar.setVisible(True)
        control.setPalette(util.palette)
        self._subWidgets.append(control)
        self._subLayout.addWidget(control)


class Notification(QtGui.QDialog):
    def __init__(self, message=None):
        """
        :param width:
        :param height:
        :return:
        """
        super(Notification, self).__init__()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self._ok = QtGui.QPushButton('Ok')
        self._ok.setMaximumWidth(50)

        self._ok.setPalette(util.dialog_palette)
        self.setStyleSheet(util.styleSheet)

        label = QtGui.QLabel(message)
        label.setPalette(util.dialog_palette)
        f = label.font()
        f.setBold(True)
        label.setFont(f)

        vertLayoutWrapper = QtGui.QVBoxLayout()
        vertLayoutWrapper.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        vertLayoutWrapper.addWidget(label)
        vertLayoutWrapper.addWidget(self._ok)

        self.setLayout(vertLayoutWrapper)

        self._ok.clicked.connect(self.accept)

    def show(self, *args, **kwargs):
        return self.exec_(*args, **kwargs)


class Dialog(QtGui.QDialog):
    def __init__(self, name=None, vertical=True, width=None, height=None, ask=None):
        """
        :param width:
        :param height:
        :return:
        """
        super(Dialog, self).__init__()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.bar = QtGui.QToolBar()
        self.customContextMenu = None
        self.widgetMenu = None
        if ask:
            self._close = QtGui.QPushButton('No')
            self._ok = QtGui.QPushButton('Yes')
        else:
            self._close = QtGui.QPushButton('Close')
            self._ok = QtGui.QPushButton('Ok')

        self._close.setPalette(util.dialog_palette)
        self._ok.setPalette(util.dialog_palette)
        self.setStyleSheet(util.styleSheet)

        if name is None:
            self._name = ''
        else:
            self._name = name
        if width is not None:
            self.setMinimumWidth(width)

        if height is not None:
            self.setMinimumHeight(height)

        if vertical:
            self._layout = QtGui.QVBoxLayout()
        else:
            self._layout = QtGui.QHBoxLayout()

        self._layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        vertLayoutWrapper = QtGui.QVBoxLayout()

        if not name == '' or not None:
            label = QtGui.QLabel(name)
            label.setPalette(util.dialog_palette)
            f = label.font()
            f.setBold(True)
            label.setFont(f)
            vertLayoutWrapper.addWidget(label)

        horLayout = QtGui.QHBoxLayout()
        horLayout.addWidget(self._ok)
        horLayout.addWidget(self._close)
        horLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

        vertLayoutWrapper.addLayout(self._layout)
        vertLayoutWrapper.addLayout(horLayout)
        vertLayoutWrapper.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self._vert = vertLayoutWrapper

        self.bar.setVisible(False)
        self.setLayout(vertLayoutWrapper)

        self._ok.clicked.connect(self.accept)
        self._close.clicked.connect(self.reject)

    def show(self, *args, **kwargs):
        return self.exec_()

    def name(self):
        """
        Name of this Widget.
        :return:
        """
        return self._name

    def contextMenuEvent(self, event):
        if self.customContextMenu:
            self.customContextMenu.exec_(self.mapToGlobal(event.pos()))
        else:
            QtGui.QWidget.contextMenuEvent(self, event)

    def addControl(self, control):
        """
        Add a control (or widget) to this Widget
        :param control:
        :return:
        """
        control.setPalette(util.dialog_palette)
        self._layout.addWidget(control)

    def removeControl(self, control):
        """
        Remove a control (or widget) from this Widget
        :param control:
        :return:
        """
        self._layout.removeWidget(control)

    def addFunction(self, functionName, func, tip=None, contextMenu=False):
        """
        Add a function to the function menu.
        :param functionName:
        :param func:
        :return:
        """
        if contextMenu:
            if not self.customContextMenu:
                self.customContextMenu = QtGui.QMenu(self)
                self.customContextMenu.setPalette(util.dialog_palette)
                self.customContextMenu.addSeparator()

            if isinstance(func, QtGui.QWidget):
                if self.widgetMenu is None:
                    self.widgetMenu = Widget()
                    layout = QtGui.QVBoxLayout()
                    menu = self.customContextMenu.addMenu('Widgets')
                    menu.setLayout(layout)
                    menu.setPalette(util.dialog_palette)
                    layout.addWidget(self.widgetMenu)
                self.widgetMenu.addControl(func)
            else:
                action = self.customContextMenu.addAction(functionName)
                action.triggered.connect(func)
                if tip is not None:
                    action.setToolTip(tip)
                    action.setStatusTip(tip)
                else:
                    action.setToolTip(func.__doc__)
                    action.setStatusTip(func.__doc__)

            return

        if isinstance(func, QtGui.QWidget):
            self.bar.addWidget(func)
        else:
            action = self.bar.addAction(functionName)
            action.triggered.connect(func)
            if tip is not None:
                action.setToolTip(tip)
                action.setStatusTip(tip)
            else:
                action.setToolTip(func.__doc__)
                action.setStatusTip(func.__doc__)
        self._vert.insertWidget(1, self.bar)
        self.bar.setVisible(True)
