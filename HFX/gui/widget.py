
# abstract class imports
from abstract import *
from control import *
from util import *

# python imports
import os
import traceback

# HFX import
import HFX

# PySide imports
from PySide import QtGui, QtCore

__all__ = [
    'ListWidget',
    'Tab',
    'LaunchWidget',
    'TreeWidget',
    'TableWidget',
    'Input',
    'FunctionDialog',
    'Notification',
    'getDirectory',
    'getFile',
    'getFilenames',
    'HUD',
    'setHudData',
    'hudData'
]


HUD_DATA = {}


class Tab(QtGui.QTabWidget):
    def __init__(self, canClose=False, canMove=False):
        """
        :return:
        """
        super(Tab, self).__init__()

        self.setPalette(palette)

    def closeAll(self):
        self.clear()

    def newTab(self, name, w=None):
        if w is None:
            w = Widget()
        self.addTab(w, name)

        return w

    def currentTab(self):
        return self.currentWidget()


class Input(Dialog):
    def __init__(self, message, title):
        super(Input, self).__init__(title)

        self._input = ShortTextInput(message)
        self.addControl(self._input)

    def value(self):
        return self._input.value()


class FunctionDialog(Dialog):
    def __init__(self):
        super(FunctionDialog, self).__init__('Function')
        HFX.blurClass(self)

        self._input = ShortTextInput('Name')
        self._input2 = IntValue('Arguments')
        self.addControl(self._input)
        self.addControl(self._input2)

    def value(self):
        return self._input.value(), self._input2.value()
HFX.blur(FunctionDialog)


class ListWidget(Widget):
    """
    List widget
    """
    def __init__(self, label=None, canEdit=False, selection=None, rowColors=None, **kwargs):
        """
        :return:
        """
        super(ListWidget, self).__init__(label, **kwargs)
        HFX.blurClass(self)

        self.allItems = []

        self.input = QtGui.QListWidget()
        self.input.setPalette(self.palette())

        if canEdit:
            self.addFunction('+', self.addItem)
            self.addFunction('-', self.removeItem)

        if selection:
            self.input.setSelectionMode(self.input.ExtendedSelection)

        if rowColors:
            self.input.setAlternatingRowColors(True)

        self.addControl(self.input)

    def _updateList(self):
        """
        --private--
        :return:
        """
        self.input.clear()

        if self.items() is None:
            return

        if isinstance(self.items(), list):
            for i in self.items():
                item = QtGui.QListWidgetItem()
                if isinstance(i, str) and i.startswith('-'):
                    item.setFlags(QtCore.Qt.NoItemFlags)
                    item.setText(i.replace('-', ' '))
                    item.setForeground(QtCore.Qt.darkGray)
                else:
                    item.setText(str(i))
                    item.setData(0, i)
                    item.setToolTip(str(i))

                self.input.addItem(item)

                size = item.sizeHint()
                size.setHeight(30)
                item.setSizeHint(size)

    def connect(self, func):
        self.input.itemClicked.connect(func)

    def value(self):
        """
        :return:
        """
        items = []
        for i in self.input.selectedItems():
            items.append(str(i.text()))

        return items

    def search(self, search=None):
        if not search:
            search = self.searchWord()
            if search is None:
                return

        items = []
        for i in range(0, len(self.items())):
            items.append(self.input.item(i))

        if search == '':
            for item in items:
                item.setHidden(False)
            return

        for item in items:
            item.setSelected(False)
            if search in item.text():
                item.setSelected(True)
                item.setHidden(False)

    def resetList(self):
        self.allItems = []
        self._updateList()

    def addItems(self, items):
        """
        Set the items to this list widget. It can be a dict or a list instance.
        :param items:
        :return:
        """
        self.allItems = items
        self._updateList()

    def items(self):
        """
        :return:
        """
        return self.allItems

    def addItem(self, item):
        """
        :return:
        """
        self.allItems.append(str(item))
        self._updateList()

    def removeItem(self, item):
        """
        :return:
        """
        target = self.items()
        for i in target:
            if i is item:
                target.remove(i)
                break

        self.allItems = target
        self._updateList()
HFX.blur(ListWidget)


class TreeWidget(Widget):
    """
    Tree Widget
    """

    red = QtCore.Qt.darkRed
    green = QtCore.Qt.darkGreen
    blue = QtCore.Qt.darkBlue
    yellow = QtCore.Qt.darkYellow
    cyan = QtCore.Qt.darkCyan
    magenta = QtCore.Qt.darkMagenta

    def __init__(self,
                 label=None,
                 headers=None,
                 canEdit=False,
                 hideHeaders=None,
                 extendedSelection=None,
                 fileSys=None,
                 **kwargs):
        super(TreeWidget, self).__init__(label, **kwargs)
        HFX.blurClass(self)

        self._items = []
        self.searchWords = []
        self.fileSys = fileSys

        if fileSys:
            self.input = QtGui.QTreeView(self)
        else:
            self.input = QtGui.QTreeWidget(self)

        self.input.setAnimated(True)
        if not canEdit:
            self.input.setSortingEnabled(True)
        else:
            self.input.setDragDropMode(self.input.InternalMove)

        if hideHeaders:
            self.input.setHeaderHidden(True)
        self.input.setExpandsOnDoubleClick(False)

        if headers is not None:
            self.input.setColumnCount(len(headers))
            self.input.setHeaderLabels(headers)

        if extendedSelection:
            self.input.setSelectionMode(self.input.ExtendedSelection)

        self.addControl(self.input)

        self.addFunction('Expand all', self.expandAll, 'Expand all items in the tree.', contextMenu=True)
        self.addFunction('Collapse all', self.collapseAll, 'Collapse all items in the tree.', contextMenu=True)

    def setPath(self, path):
        """
        Set the path if this is a file system viewer.
        :param path:
        :return:
        """
        self.fileSys = QtGui.QFileSystemModel()
        self.fileSys.setRootPath(path)
        self.input.setModel(self.fileSys)
        self.input.setRootIndex(self.fileSys.index(path))

    def itemOrder(self):
        above = self.input.topLevelItem(0)

        expandPast = {}
        for item in self.items():
            expandPast[item] = item.isExpanded()

        self.expandAll()

        order = []

        content = []
        for col in range(0, self.input.columnCount()):
            content.append(str(above.text(col)))
        order.append(content)

        while 1:
            above = self.input.itemBelow(above)
            if above is None:
                break

            content = []
            for col in range(0, self.input.columnCount()):
                content.append(str(above.text(col)))

            order.append(content)

        for item in expandPast:
            item.setExpanded(expandPast[item])

        return order

    def sort(self, col):
        self.input.sortByColumn(col, QtCore.Qt.AscendingOrder)

    def recursiveExpand(self, item):
        if item is None:
            return
        if item.parent() is self.input:
            return
        else:
            item.setExpanded(True)
            item.setHidden(False)
            self.recursiveExpand(item.parent())

    def search(self, search=None):
        for item in self._items:
            try:
                item.setHidden(False)
                item.setHidden(True)
            except RuntimeError:
                self._items.pop(self._items.index(item))
        if not search:
            search = self.searchWord()

        if search == '':
            for item in self._items:
                item.setHidden(False)
            return

        self.input.collapseAll()

        for item in self._items:
            if search == '':
                item.setHidden(False)
                continue

            item.setSelected(False)

            if item.childCount() == 0:
                item.setHidden(True)

            for col in xrange(0, self.input.columnCount()):
                if not item.text(col):
                    continue

                if search.lower() in item.text(col).lower():
                    item.setSelected(True)
                    self.recursiveExpand(item)
                    item.setHidden(False)
                    break

    def findItem(self, name, column=None):
        """
        Find an item by text
        :param name:
        :param column:
        :return:
        """
        if not column:
            column = 0

        for i in self._items:
            if i.text(column) == name:
                return i

    def clear(self):
        """
        Clear the tree
        :return:
        """
        self._items = []
        self.input.clear()

    def collapseAll(self):
        self.input.collapseAll()

    def expandAll(self):
        """
        Expand all items in tree widget.
        :return:
        """
        self.input.expandAll()

    def resize(self):
        """
        Resize all columns to fit the contents
        :return:
        """
        for col in range(0, self.input.columnCount()):
            self.input.resizeColumnToContents(col)

        for item in self.items():
            for col in range(0, self.input.columnCount()):
                size = item.sizeHint(col)
                size.setHeight(30)
                item.setSizeHint(col, size)

    def addItem(self, text, parent=None, column=None, color=None, widgets=None):
        """
        Add an item to the tree widget.
        :param widgets:
        :param color:
        :param column:
        :param text: list of text data.
        :param parent:
        :return:
        """
        if parent is None:
            parent = self.input

        item = QtGui.QTreeWidgetItem(parent)

        if isinstance(text, str) and column is not None or isinstance(text, unicode) and column is not None:
            item.setText(column, str(text))

        elif isinstance(text, str) or isinstance(text, unicode):
            item.setText(0, str(text))

        else:
            column = 0
            for t in text:
                item.setText(column, str(t))
                column += 1

        self._items.append(item)

        if isinstance(text, list):
            for t in text:
                if str(t) not in self.searchWords:
                    self.searchWords.append(str(t))
                    self.setKeywords(self.searchWords)

        else:
            if text not in self.searchWords:
                self.searchWords.append(text)
                self.setKeywords(self.searchWords)

        if color:
            if column:
                item.setBackground(column, color)
            else:
                item.setBackground(0, color)

        if widgets:
            column = 0
            for widget in widgets:
                if widget is None:
                    column += 1
                    continue
                widget.setParent(self.input)
                self.input.setItemWidget(item, column, widget)
                column += 1

        return item

    def removeItem(self, item):
        """
        Remove an item from the tree widget
        :param item:
        :return:
        """
        count = 0
        for i in xrange(0, len(self._items)):
            if self._items[count] is item:
                self._items.pop(count)
                break
            count += 1

        parent = item.parent()
        if parent is None:
            self.input.takeTopLevelItem(self.input.indexOfTopLevelItem(item))
        else:
            parent.takeChild(parent.indexOfChild(item))

    def getWidget(self, item, column):
        return self.input.itemWidget(item, column)

    def removeWidget(self, item, column):
        self.input.removeItemWidget(item, column)

    def setItemWidget(self, item, column, widget):
        widget.setParent(self.input)
        self.input.setItemWidget(item, column, widget)

    def connect(self, func):
        self.input.itemDoubleClicked.connect(func)

    def value(self, items=None):
        """
        Returns a dict containing the values of the current selection.
        :return:
        """
        if self.fileSys:
            return self.fileSys.filePath(self.input.selectedIndexes()[0])

        if items:
            return self.input.selectedItems()

        value = {}

        for i in self.input.selectedItems():
            value[i.text(0)] = []
            for col in xrange(1, self.input.columnCount()):
                value[i.text(0)].append(i.text(col))

        return value

    def items(self):
        return self._items
HFX.blur(TreeWidget)


class TableWidget(Widget):
    Rows = 0
    Columns = 1

    def __init__(self, label=None, headers=None, hideHeaders=None, **kwargs):
        super(TableWidget, self).__init__(label, **kwargs)
        HFX.blurClass(self)

        self.items = []

        self.input = QtGui.QTableWidget(self)
        self.addControl(self.input)

    def deleteRow(self):
        """
        Delete a row
        """
        self.input.removeRow(self.input.currentRow())

    def clear(self):
        """
        Clear the table
        """
        self.items = []
        self.input.clear()

    def value(self, how=None):
        """
        Return the value of the table.
        """
        if how is not None:
            if how == self.Rows:
                package = {}
                for row in xrange(0, self.input.rowCount()):
                    package[row] = []
                    for column in xrange(0, self.input.columnCount()):
                        package[row].append(self.input.item(row, column))

                return package

            if how == self.Columns:
                package = {}
                for column in xrange(0, self.input.columnCount()):
                    package[column] = []
                    for row in xrange(0, self.input.rowCount()):
                        package[column].append(self.input.item(row, column))
                return package

        return self.items

    def addItem(self, text, row, column):
        """
        Add an item to the table
        """

        if row + 1 > self.input.rowCount():
            self.input.setRowCount(row)

        if column + 1 > self.input.columnCount():
            self.input.setColumnCount(column)

        item = QtGui.QTableWidgetItem()
        self.items.append(item)
        self.input.setItem(row, column, item)
        item.setText(text)
HFX.blur(TableWidget)


class LaunchWidget(Widget):
    """
    Launch widget
    """
    def __init__(self):
        super(LaunchWidget, self).__init__('Applications')
        HFX.blurClass(self)

        self.environment = None

        applications = []
        for app in os.listdir(HFX.environmentDirectory()):
            if app.endswith('.env'):
                applications.append(app)

        container = Tab()
        launcher = container.newTab('Launcher')
        settings = container.newTab('Advanced')

        self.appBox = OptionBox('', applications, allowNone=True, searchable=True, width=150)
        self.launchArgs = ShortTextInput('Launch Arguments')
        self.withPython = Toggle('Python')
        self.withPython.setValue(True)
        self.button = Button('Launch')

        launcher.addControl(self.appBox)
        launcher.addControl(self.button)
        settings.addControl(self.launchArgs)

        self.addControl(container)
        self.button.addControl(self.withPython)

        self.button.connect(self.launch)
        self.appBox.connect(self._extractEnv)

    def _extractEnv(self):
        env = HFX.loadEnvironment(self.appBox.value())
        if env is None:
            self.launchArgs.setValue('')
        else:
            self.launchArgs.setValue(env['HFX_APP_ARGS'])

    def launch(self):
        if self.appBox.value() == '':
            return

        os.environ['HFX_APP'] = self.appBox.value()
        os.environ['HFX_APP_ARGS'] = self.launchArgs.value()

        if HFX.loadEnvironment(self.appBox.value())['HFX_GUI']:
            os.environ['HFX_GUI'] = 'true'

        HFX.executeHFX(self.withPython.value())
HFX.blur(LaunchWidget)


class HUD(QtGui.QWidget):
    """
    HUD element for quick access to certain functions.
    """
    def __init__(self):
        """
        Pass a dictionary that will map out the data to be displayed in the HUD
        :param hudMap:
        """
        super(HUD, self).__init__(None,
                                  QtCore.Qt.FramelessWindowHint |
                                  QtCore.Qt.WindowSystemMenuHint |
                                  QtCore.Qt.WindowStaysOnTopHint
                                  )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        HFX.blurClass(self)

        # UI data
        self._clickPos = None
        self._key = None
        self._group = None
        self._functions = {}
        self._currentFunction = ''

        #self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            click = self.mapFromGlobal(event.globalPos())
            self._clickPos = QtCore.QPoint(click.x() - (self.width() / 2), click.y() - (self.height() / 2))
            self.repaint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def keyPressEvent(self, event):
        self._key = event.key() - 48
        self.repaint()

    def keyReleaseEvent(self, event):
        try:
            if event.key() != 16777221:
                try:
                    self._currentFunction = self._functions[self._key]
                    self.repaint()
                    return
                except KeyError:
                    self._currentFunction = None
                    self.repaint()
                    return
            try:
                HUD_DATA[self._group][self._currentFunction]()
            except KeyError:
                self.repaint()
                return
        except:
            HFX.Notification(traceback.format_exc()).show()
            self.repaint()
            return
        self.repaint()

    def mousePoint(self):
        return self._clickPos

    def paintEvent(self, event):
        # set up painter object
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)

        # draw tool groups
        angle = 360 / len(HUD_DATA)
        size = 180
        rect = QtCore.QRect(-(size / 2), size / 2, size, -size)
        outRadialCopy = QtCore.QRect(-(size / 2) * .50, (size / 2) * .50, size * .50, -size * .50)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 50, 100, 100)))
        pen = painter.pen()
        painter.setPen(QtCore.Qt.NoPen)

        painter.drawEllipse(outRadialCopy)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 80, 50, 80)))

        line = QtCore.QLineF(0, 0, 60, 0)
        rotation = angle
        for group in sorted(HUD_DATA):
            painter.setPen(QtCore.Qt.NoPen)
            line.setAngle(rotation + (angle / 2))

            rect.moveCenter(QtCore.QPoint(0, 0))

            mouseMap = QtCore.QRect(line.p2().toPoint().x() - 25, line.p2().toPoint().y() - 25, 50, 50)
            paintOps = False
            painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 80, 50, 80)))
            if self.mousePoint() is not None:
                if mouseMap.contains(self.mousePoint()):
                    paintOps = True
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 120, 50, 100)))
                    self._group = group

            if self._currentFunction is not None:
                if self._currentFunction in HUD_DATA[group]:
                    paintOps = True
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(50, 120, 50, 100)))
                    self._group = group

            painter.drawPie(rect, (rotation + 5) * 16, (angle - 10) * 16)
            rect.moveCenter(line.p2().toPoint())

            painter.setPen(pen)

            if paintOps:
                branch = QtCore.QLineF()
                branch.setP1(rect.center())
                branch.setLength(70)
                branch.setAngle(line.angle())

                if branch.p1().x() < branch.p2().x():
                    branch.setP2(QtCore.QPoint(110, branch.p2().y()))

                painter.drawLine(branch)

                data = HUD_DATA[group]

                if isinstance(data, list) and len(data) != 0 or isinstance(data, dict) and len(data) != 0:
                    yOffset = False
                    yDirection = 1
                    secLength = -len(data)
                    if branch.p1().y() <= branch.p2().y():
                        yOffset = True
                        yDirection = -1
                        secLength = len(data)

                    xOffset = False
                    if branch.p1().x() > branch.p2().x():
                        xOffset = True

                    step = 20 * yDirection

                    pointX = branch.p2().x()
                    pointY = branch.p2().y()

                    if xOffset:
                        wrapper = QtCore.QLineF()
                        wrapper.setP1(QtCore.QPoint(pointX, pointY))
                        wrapper.setP2(QtCore.QPoint(110, pointY))
                        painter.drawLine(wrapper)

                        pointX = wrapper.p2().x()
                        pointY = wrapper.p2().y()

                    sectionLine = QtCore.QLineF()
                    sectionLine.setP1(QtCore.QPoint(pointX, pointY))
                    sectionLine.setAngle(90)
                    sectionLine.setLength(secLength * 12)

                    painter.drawLine(sectionLine)

                    revert = painter.pen()

                    if isinstance(data, dict):
                        funcIndex = 0
                        self._functions = {}

                        # draw list data
                        for entry in sorted(data):
                            painter.setPen(revert)
                            offset = 10
                            if yOffset:
                                offset = -10
                            stringData = str(entry)
                            function = data[entry]
                            if function is not None:
                                funcPen = QtGui.QPen()
                                funcPen.setColor(QtGui.QColor(100, 100, 150))
                                if self._currentFunction == stringData:
                                    funcPen.setColor(QtCore.Qt.green)
                                painter.setPen(funcPen)
                                painter.drawText(pointX + 5, pointY + offset, str(funcIndex) + ': ' + stringData)
                                self._functions[funcIndex] = stringData
                            else:
                                painter.drawText(pointX + 5, pointY + offset, stringData)

                            funcIndex += 1
                            pointY += step

                    else:
                        for entry in sorted(data):
                            stringData = str(entry)
                            painter.drawText(pointX + 5, pointY, stringData)
                            pointY += step

                    painter.setPen(revert)

            painter.drawText(rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, str(group))

            rotation += angle

        if self._currentFunction is not None:
            painter.drawText(outRadialCopy, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, str(self._currentFunction))

    def sizeHint(self):
        return QtCore.QSize(2000, 2000)
HFX.blur(HUD)


def setHudData(data):
    """
    Set the HUD dictionary
    :param data:
    :return:
    """
    global HUD_DATA
    HUD_DATA = data


def hudData():
    """
    Return the current HUD dictionary
    :return:
    """
    return HUD_DATA


def getDirectory():
    return str(QtGui.QFileDialog.getExistingDirectory())


def getFile():
    return str(QtGui.QFileDialog.getOpenFileName())


def getFilenames():
    return str(QtGui.QFileDialog.getOpenFileNames())
