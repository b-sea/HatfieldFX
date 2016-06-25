
# PySide imports
from PySide import QtGui, QtCore


__all__ = [
    'GraphicsNode',
]


class GraphicsNode(QtGui.QGraphicsItem):
    """
    Basic graphics item to be added to GraphicsWidgets.
    """

    Rectangle, Radial = range(0, 2)

    def __init__(self, name, width=150, height=30, inputs=None, outputs=None, position=None, defaultOutput=True, color=None):
        """
        :return:
        """
        super(GraphicsNode, self).__init__()

        self._name = name
        self._width = width
        self._height = height
        self.connections = []
        self._DoubleClickFunction = None
        self._data = {}
        self._color = color

        self._activeTerminal = None
        self._terminalPoints = {}

        self._inputs = {}
        self._outputs = {}

        if inputs:
            for input in inputs:
                self._inputs[input] = []

        if defaultOutput:
            self._outputs['output'] = []

        if outputs:
            for output in outputs:
                self._outputs[output] = []

        self._height = height * max(len(self._outputs.keys()), len(self._inputs.keys())) + height

        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

        if position is not None:
            self.setPos(position[0], position[1])

        self.update()

    def position(self):
        return self.pos().x(), self.pos().y()

    def inputs(self):
        return self._inputs

    def outputs(self):
        return self._outputs

    def name(self):
        return self._name

    def setDoubleClickFunction(self, function):
        self._DoubleClickFunction = function

    def dataKeys(self):
        return self._data.keys()

    def setData(self, key, data):
        self._data[key] = data

    def rawData(self):
        return self._data

    def data(self, key):
        data = self._data[key]
        return data

    def hold(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)

    def release(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

    def terminal(self, point):
        """
        Pick terminal
        """
        for terminal in self._terminalPoints:
            if self._terminalPoints[terminal].contains(self.mapFromScene(point).x(), self.mapFromScene(point).y()):
                return terminal

    def mousePressEvent(self, event):
        """
        Mouse press event override for highlighting.
        """
        for terminal in self._terminalPoints.keys():
            rect = self._terminalPoints[terminal]
            if rect.contains(event.pos().x(), event.pos().y()):
                self._activeTerminal = terminal
                self.update()
                self.hold()
                self.scene().enterConnectionMode(self.mapToScene(self.mapFromItem(self, rect.center())))
                return

        self._activeTerminal = None
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Mouse press event override for highlighting.
        """
        self._activeTerminal = None
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

        self.release()
        self.update()

    def mouseDoubleClickEvent(self, event):
        terminal = self.terminal(self.mapToScene(event.pos()))
        if terminal:
            for connection in self.connections:
                if connection.connected[self] == terminal:
                    connection.disconnect()
                    self.scene()._deleted.append(connection)
                    return

        if self._DoubleClickFunction:
            self._DoubleClickFunction(self)

    def connect(self, thisTerminal, node, thatTerminal):
        return Connection(self, node, thisTerminal, thatTerminal)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget):
        pen = painter.pen()
        gradient = QtGui.QLinearGradient(0, 0, 0, self._height)
        if self._color:
            gradient.setColorAt(0, QtGui.QColor(self._color[0], self._color[1], self._color[2], 200))
            gradient.setColorAt(1, QtGui.QColor(self._color[0]/2, self._color[1]/2, self._color[2]/2, 200))
        else:
            gradient.setColorAt(0, QtGui.QColor(70, 70, 90, 200))
            gradient.setColorAt(1, QtGui.QColor(30, 30, 30, 200))

        if self.isSelected():
            painter.setPen(QtGui.QColor(100, 100, 120))
        else:
            painter.setPen(QtGui.QColor(70, 70, 90))

        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawRoundedRect(0, 0, self._width, self._height, 7.5, 7.5)

        painter.setPen(QtCore.Qt.white)
        painter.drawText(QtCore.QRect(0, 5, self._width, 15), QtCore.Qt.AlignCenter, self._name)
        painter.setPen(QtGui.QColor(70, 70, 90))

        painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 130, 80)))

        offset = (len(self._inputs) / self._height) + 30
        size = 10
        highlighter = QtGui.QColor(100, 100, 120)

        for input in sorted(self._inputs.keys()):
            if not self._activeTerminal is None and input == self._activeTerminal:
                painter.setPen(highlighter)
            else:
                painter.setPen(QtGui.QColor(70, 70, 90))

            terminal = QtCore.QRect(0, offset, size, size)
            painter.drawRect(terminal)
            self._terminalPoints[input] = terminal
            painter.setPen(QtCore.Qt.white)
            painter.drawText(QtCore.QRect(size + 5, offset, self._width - (size*2), (size*2)), QtCore.Qt.AlignLeft, input)
            offset += 30

        painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 50, 50)))

        offset = (len(self._outputs) / self._height) + 30

        for output in sorted(self._outputs.keys()):
            if not self._activeTerminal is None and output == self._activeTerminal:
                painter.setPen(highlighter)
            else:
                painter.setPen(QtGui.QColor(70, 70, 90))
            terminal = QtCore.QRect(self._width - size, offset, size, size)
            painter.drawRect(terminal)
            self._terminalPoints[output] = terminal
            painter.setPen(QtCore.Qt.white)
            painter.drawText(QtCore.QRect(size - 5, offset, self._width - (size*2), size*2), QtCore.Qt.AlignRight, output)
            offset += 30

        painter.setPen(pen)

        for connection in self.connections:
            connection.getTerminalScenePositions()


class Connection(QtGui.QGraphicsLineItem):
    """
    Connection item.
    """
    def __init__(self, nodeA, nodeB, terminalA, terminalB):
        super(Connection, self).__init__()

        # Store nodes
        self.nodeA = nodeA
        self.nodeB = nodeB

        self.terminalAid = terminalA
        self.terminalBid = terminalB

        self.connected = {
            nodeA: terminalA,
            nodeB: terminalB
        }

        self.setZValue(-1)

        pen = QtGui.QPen()

        pen.setWidth(1)
        pen.setBrush(QtGui.QColor(50, 80, 50))
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)

        self.setPen(pen)

        self.nodeA.connections.append(self)
        self.nodeB.connections.append(self)

        if terminalA not in self.nodeA._inputs:
            self.nodeA._outputs[terminalA].append(self.nodeB)
        else:
            self.nodeA._inputs[terminalA].append(self.nodeB)

        if terminalB not in self.nodeB._inputs:
            self.nodeB._outputs[terminalB].append(self.nodeA)
        else:
            self.nodeB._inputs[terminalB].append(self.nodeA)

    def disconnect(self):
        self.nodeA.connections.pop(self.nodeA.connections.index(self))
        self.nodeB.connections.pop(self.nodeB.connections.index(self))

        try:
            self.scene().removeItem(self)
        except AttributeError:
            return

    def getTerminalScenePositions(self):
        # Store terminal id information.
        try:
            self.terminalA = self.mapFromItem(self.nodeA, self.nodeA._terminalPoints[self.terminalAid].center())
            self.terminalB = self.mapFromItem(self.nodeB, self.nodeB._terminalPoints[self.terminalBid].center())
            self.setLine(self.terminalA.x(), self.terminalA.y(), self.terminalB.x(), self.terminalB.y())
        except KeyError:
            pass
