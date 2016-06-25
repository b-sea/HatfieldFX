# PySide import
from PySide import QtGui, QtCore

# python imports
from os.path import basename
from functools import partial

# hfx gui imports
import instance


__all__ = [
    '_hfx',
    'toHFX',
    'applyHFXStyle',
    'Vertical',
    'Horizontal'
]


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
Horizontal = QtGui.QHBoxLayout

class _hfx(QtGui.QWidget):
    """
    --container widget--

    This is the underlying widget that will handle all layout manipulations
    """
    def __init__(self, mainWidget, layout):
        super(_hfx, self).__init__()

        # HFX required variables
        self._name = ''
        self._layout = None
        self._widgets = []
        self._toolTips = {}
        self._functions = {}
        self._contextFunctions = {}
        self._contextMap = []
        self._mainWidget = mainWidget

        # assign hfx layout functions
        self._mainWidget._hfx = self
        self._mainWidget.name = self.name
        self._mainWidget.setName = self.setName
        self._mainWidget.widgets = self.widgets
        self._mainWidget.addWidget = self.addWidget
        self._mainWidget.removeWidget = self.removeWidget
        self._mainWidget.thisWidget = self.thisWidget
        self._mainWidget.functions = self.functions
        self._mainWidget.addFunction = self.addFunction
        self._mainWidget.removeFunction = self.removeFunction
        self._mainWidget.addContextFunction = self.addContextFunction
        self._mainWidget.addContextSplit = self.addContextSplit
        self._mainWidget.contextMenuEvent = self.hfxMenuEvent
        self._mainWidget.getToolTip = self.getToolTip
        self._mainWidget.show = self.show

        # define the layout type
        self._layout = layout(self)
        self._layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(self._layout)

        # add the main widget to the layout
        self._layout.addWidget(self._mainWidget)

        # set up styling
        applyHFXStyle(self)
        applyHFXStyle(self._mainWidget)

    def show(self):
        if QtGui.qApp.applicationName() == 'python':
            toolBar = QtGui.QToolBar()
            toolBar.setOrientation(QtCore.Qt.Vertical)
            for function in sorted(self.functions()):
                func = self.functions()[function]
                if isinstance(func, QtGui.QWidget):
                    toolBar.addWidget(func)
                else:
                    action = toolBar.addAction(basename(function))
                    action.triggered.connect(func)

            for widget in self.widgets():
                for function in sorted(widget.functions()):
                    func = widget.functions()[function]
                    if isinstance(func, QtGui.QWidget):
                        toolBar.addWidget(func)
                    else:
                        action = toolBar.addAction(basename(function))
                        action.triggered.connect(func)

            self._layout.insertWidget(0, toolBar)
        instance.waitTillClose(self)

    def hfxMenuEvent(self, event):
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
            type(self._mainWidget).contextMenuEvent(self._mainWidget, event)

    def name(self):
        """
        Return the name of this widget
        :return:
        """
        return self._name

    def setName(self, name):
        """
        Set the name of this widget
        :return:
        """
        self._name = name

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
        return self

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
        else:
            self._functions[url] = partial(function, *args, **kwargs)

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


def applyHFXStyle(widget):
    widget.setStyle(QtGui.QStyleFactory().create('Plastique'))  #windowsvista
    widget.setStyleSheet(instance.hfxStylesheet())


def toHFX(widget, layout=Vertical):
    """
    Converts an existing PySide widget to an HFX widget.
    :param layout: layout type example: HFX.Vertical
    :param widget: PySide widget
    :return: PySide widget
    """
    _hfx(mainWidget=widget, layout=layout)
    return widget
