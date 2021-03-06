# PySide import
from PySide import QtGui, QtCore, __version__

# python imports
from os.path import basename
from functools import partial
import logging

# hfx gui imports
import instance


__all__ = [
    'ConvertToHFX',
    'applyHFXStyle',
    'Vertical',
    'Horizontal',
    'guiKitVersion'
]


def guiKitVersion():
    """
    Get the version of PySide that the gui kit is using.
    :return:
    """
    logging.info('PySide')
    logging.info('Version: ' + __version__)
    logging.info('Compiled with: Qt ' + QtCore.__version__)
    logging.info('Using: Qt ' + QtCore.qVersion())


# Functions required for HFX Widgets conversion:
#   .name()
#   .setName(name)
#   .widgets()
#   .addWidget(widget)
#   .functions()
#   .addFunction(url, function)

# Variables required for HFX Widget conversion:
#   ._name
#   ._layout
#   ._hfx
#   ._widgets
#   ._functions
#   ._mainWidget

# layout presets
Vertical = QtGui.QVBoxLayout
Horizontal = QtGui.QToolBar


class ConvertToHFX(object):
    """
    HFX object that handles most layout manipulations and tedious override functions from PySide.
    """
    def __init__(self, label=None, layout=None, isDialog=None):
        super(ConvertToHFX, self).__init__()

        # HFX required variables
        self._name = ''
        self._layout = None
        self._widgets = []
        self._toolTips = {}
        self._functions = {}
        self._contextFunctions = {}
        self._contextMap = []
        self._funcBar = QtGui.QToolBar()
        self._hfx = QtGui.QWidget()
        self._HeaderAndFooter = Vertical()
        self._hfx.isHFX = self.isHFX
        self._hfx.functions = self.functions
        applyHFXStyle(self._hfx)

        if layout:
            self._layout = layout()
        else:
            self._layout = Vertical()

        # Build layout
        self._HeaderAndFooter.addWidget(self._funcBar)
        if isinstance(self._layout, Horizontal):
            self._HeaderAndFooter.addWidget(self._layout)
        else:
            self._HeaderAndFooter.addLayout(self._layout)
            self._layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # align
        self._HeaderAndFooter.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        if label:
            self.setName(label)

        # add the main widget to the layout
        if isDialog:
            self.setLayout(self._HeaderAndFooter)
        else:
            self._hfx.setLayout(self._HeaderAndFooter)
            self._layout.addWidget(self)

        applyHFXStyle(self)

    def isHFX(self):
        return True

    def _inHFXApplication(self):
        """
        --private--
        :return:
        """
        for action in self._funcBar.actions():
            if isinstance(action, QtGui.QWidgetAction):
                continue
            self._funcBar.removeAction(action)

        if not self._funcBar.actions():
            self._funcBar.setVisible(False)
        else:
            self._funcBar.setVisible(True)

    def connectTo(self, function, *args):
        """
        Pass a function with a list of signals you want to tie it to or pass a signal you want to tie a list of
            functions to.
        :param function:
        :param args:
        :return:
        """
        if isinstance(function, QtCore.Signal):
            for func in args:
                function.connect(func)
        else:
            for signal in args:
                signal.connect(function)

    def addHeader(self, widget):
        """
        Add a widget to the header of this widget.
        :param widget:
        :return:
        """
        widget = instance.validateWidgetLayout(widget)
        self._HeaderAndFooter.insertWidget(0, widget)
        self._widgets.append(widget)

    def addFooter(self, widget):
        """
        Add a widget to the footer of this widget.
        :param widget:
        :return:
        """
        widget = instance.validateWidgetLayout(widget)
        self._HeaderAndFooter.insertWidget(self._HeaderAndFooter.count(), widget)
        self._widgets.append(widget)

    def contextMenuEvent(self, event):
        """
        Custom right click
        :param event:
        :return:
        """
        if self._contextMap:

            # build menu
            contextMenu = QtGui.QMenu(self)

            subMenus = {}

            # loop through all registered functions
            for function in self._contextMap:

                if function == '/':
                    contextMenu.addSeparator()
                    continue

                if '/' not in function:
                    if function:
                        action = contextMenu.addAction(function)
                        action.triggered.connect(self._contextFunctions[function])
                    else:
                        contextMenu.addSeparator()

                else:
                    currentPath = ''
                    base = basename(function)
                    for part in function.split('/'):
                        if part == '':
                            continue

                        if part == base:
                            func = self._contextFunctions[function]
                            if func is None:
                                subMenus[currentPath].addSeparator()
                            else:
                                action = subMenus[currentPath].addAction(base)
                                action.triggered.connect(self._contextFunctions[function])

                            continue

                        currentPath += '/' + part
                        if currentPath not in subMenus:
                            subMenus[currentPath] = contextMenu.addMenu(part)

            contextMenu.exec_(self.mapToGlobal(event.pos()))

        else:
            type(self._hfx).contextMenuEvent(self, event)

    def name(self):
        """
        Return the name of this widget
        :return:
        """
        return self._name

    def setName(self, name):
        """
        Set the name of this widget. This will also add a header label to the widget with the name as well.
        :return:
        """
        self._name = name
        self.addHeader(QtGui.QLabel(self.name()))

    def widgets(self):
        """
        Get a list of all widgets in this widgets layout.
        :return:
        """
        return self._widgets

    def addWidget(self, widget, index=None):
        """
        Add a widget to this widget
        :return:
        """
        widget = instance.validateWidgetLayout(widget)

        if widget in self._widgets:
            return

        # add to the layout.
        if index is not None:
            self._layout.insertWidget(index, widget)
        else:
            self._layout.addWidget(widget)

        self._widgets.append(widget)

    def removeWidget(self, widget):
        """
        Remove a widget from this widget
        :return:
        """
        instance.validateWidgetLayout(widget)

        if widget not in self._widgets:
            return

        # remove to the layout.
        self._layout.removeWidget(widget)
        self._widgets.pop(self._widgets.index(widget))

    def thisWidget(self):
        """
        Get this widgets layout handler so it can be added to other widgets.
        :return:
        """
        return self._hfx

    def functions(self):
        """
        Get a dictionary containing this widgets functions
        :return:
        """
        return self._functions

    def addFunction(self, url, function, tip=None, *args, **kwargs):
        """
        Add a function to this widget. You can pass optional arguments as well.
        :param url:
        :param function:
        :param tip:
        :param args:
        :return:
        """
        if isinstance(function, QtGui.QWidget):
            self._functions[url] = function
            self._funcBar.addWidget(self._functions[url])
        else:
            self._functions[url] = partial(function, *args, **kwargs)
            action = self._funcBar.addAction(url)
            action.triggered.connect(self._functions[url])

        self._funcBar.setVisible(True)
        self._toolTips[url] = tip

    def getToolTip(self, url):
        """
        Get a tool tip for a function
        :param url:
        :return:
        """
        if url in self._toolTips:
            if self._toolTips[url]:
                return self._toolTips[url]
        return ''

    def addContextFunction(self, name, function, tip=None, *args, **kwargs):
        """
        Add a function to this widgets context menu. You can pass optional arguments as well.
        :param name:
        :param function:
        :param args:
        :return:
        """
        self._contextMap.append(name)
        self._contextFunctions[name] = partial(function, *args, **kwargs)
        self._toolTips[name] = tip

    def addContextSplit(self, path='/'):
        """
        Add a split to this widgets context menu.
        :return:
        """
        self._contextMap.append(path)
        self._contextFunctions[path] = None

    def removeFunction(self, url):
        """
        Remove a function from this widget.
        :param url:
        :return:
        """
        del self._functions[url]

    def show(self):
        self._hfx.show()


def applyHFXStyle(widget):
    widget.setStyle(QtGui.QStyleFactory().create('Plastique'))
    widget.setStyleSheet(instance.hfxStylesheet())

