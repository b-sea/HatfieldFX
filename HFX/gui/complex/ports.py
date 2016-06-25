# python imports
import math

# Widget import
from HFX.gui.abstract import Widget
from HFX.gui.util import palette

# package imports
from graphics import GraphicsNode, Connection

# PySide imports
from PySide import QtGui
from PySide.QtGui import *
from PySide.QtCore import *

__all__ = ['Scene', 'NodeGraph', 'GraphicsWidget']


class Scene(QGraphicsScene):
    def __init__(self):
        super(Scene, self).__init__()
        self.ops = []
        self._deleted = []

        self._line = None
        self._lineObject = None
        self._connectionMode = False

    def enterConnectionMode(self, startPoint):
        """
        --private--
        """
        self._line = QLineF()
        self._line.setP1(startPoint)
        self._connectionMode = True

    def getContextItem(self, point):
        """
        Get the item that the mouse is currently over.
        """
        for op in self.ops:
            try:
                if op.mapRectToScene(op.boundingRect()).contains(point):
                    return op
            except:
                return None

    def getNode(self, name):
        """
        Get a node by its name.
        :param name:
        :return:
        """
        for item in self.items():
            if not isinstance(item, GraphicsNode):
                continue
            if item.name() == name:
                return item

    def allOps(self):
        """
        Get all ops.
        """
        self.ops = []
        for item in self.items():
            if isinstance(item, GraphicsNode):
                self.ops.append(item)

        return self.ops

    def keyPressEvent(self, event):
        """
        Key press events.
        :param event:
        :return:
        """
        #view object
        view = self.views()[0]

        #Keys and event management.
        if event.key() == Qt.Key_Alt:
            view.setDragMode(QGraphicsView.ScrollHandDrag)

        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            for item in self.selectedItems():
                if isinstance(item, Connection):
                    del item

    def keyReleaseEvent(self, event):
        """
        Key release events.
        :param event:
        :return:
        """
        #view object
        view = self.views()[0]

        #Keys and event management.
        if event.key() == Qt.Key_Alt:
            view.setDragMode(QGraphicsView.RubberBandDrag)

    def mouseMoveEvent(self, event):
        """
        Check draw modes.
        """
        if self._connectionMode:
            self._line.setP2(event.scenePos())
            if self._lineObject is None:
                self._lineObject = self.addLine(self._line)
                self._lineObject.setPen(QPen(QBrush(Qt.gray), 2))
                self._lineObject.setZValue(-1)

            self._lineObject.setLine(self._line)

        for item in self.items():
            if isinstance(item, Connection):
                item.getTerminalScenePositions()

        QGraphicsScene.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Release
        """
        targetOp = self.getContextItem(event.scenePos())
        if targetOp is None:
            if not self._line is None:
                self.removeItem(self._lineObject)

            self._line = None
            self._lineObject = None
            self._connectionMode = False
        elif self._line is None:
            pass
        else:
            sourceOp = self.getContextItem(self._line.p1())
            sourceTerminal = sourceOp.terminal(self._line.p1())
            targetTerminal = targetOp.terminal(event.scenePos())

            if not targetTerminal is None:
                self.addItem(Connection(sourceOp, targetOp, sourceTerminal, targetTerminal))

            if not self._line is None:
                self.removeItem(self._lineObject)

            self._line = None
            self._lineObject = None
            self._connectionMode = False

        QGraphicsScene.mouseReleaseEvent(self, event)

    def addItem(self, *args, **kwargs):
        QGraphicsScene.addItem(self, *args, **kwargs)
        self.allOps()


class NodeGraph(QGraphicsView):
    """
    Basic node graph view.
    """

    def __init__(self):
        super(NodeGraph, self).__init__()

        # self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self.nodeHooks = []

        self.setScene(Scene())

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)

    def setNodeHook(self, func):
        """
        Add a function to be added to each node when double clicked.
        :param func:
        :return:
        """
        self.nodeHooks.append(func)

    def deleteNodes(self, nodes=None):
        """
        Delete nodes from graph.
        """
        if nodes is None:
            self.scene().removeItems(self.scene().selectedItems())
        else:
            self.scene().removeItems(nodes)
        self.scene().allOps()


class GraphicsWidget(Widget):
    """
    Base class for all HFX graphic types.
    """

    def __init__(self, name=None):
        super(GraphicsWidget, self).__init__(name)

        self._view = NodeGraph()
        self._view.setPalette(palette)
        self._scene = self._view.scene()

        self.addControl(self._view)

    def find(self, name):
        """
        Find a graphics item by its name.
        :param name:
        :return:
        """
        for item in self._scene.items():
            try:
                if name == item.name():
                    return item
            except AttributeError:
                continue

    def loadNodes(self, nodes):
        for node in nodes:
            gfxNode = GraphicsNode(name=node['name'], inputs=node['inputs'], outputs=node['outputs'],
                                   position=node['pos'], defaultOutput=False, color=node['color'])

            if 'data' in node:
                for dataKey in node['data']:
                    gfxNode.setData(dataKey, node['data'][dataKey])

            self.addGraphic(gfxNode)

    def loadConnections(self, connections):
        for connection in connections:
            self.addGraphic(Connection(self.find(connection['nodeA']), self.find(connection['nodeB']),
                                       connection['terminalA'], connection['terminalB']))

    def allGraphics(self):
        pack = []
        for item in self._scene.items():
            if not isinstance(item, GraphicsNode):
                continue

            node = dict(name=item.name(), inputs=item._inputs.keys(), outputs=item._outputs.keys(), pos=item.position(),
                        width=item._width, height=item._height, data=item.rawData(), color=item._color)

            pack.append(node)

        return pack

    def allConnections(self):
        pack = []
        for item in self._scene.items():
            if not isinstance(item, Connection):
                continue

            if item.nodeA.name() == item.nodeB.name():
                self._scene.removeItem(item)
                del item
                continue

            connect = {
                'nodeA': item.nodeA.name(), 'nodeB': item.nodeB.name(), 'terminalA': item.terminalAid,
                'terminalB': item.terminalBid,
            }

            pack.append(connect)

        return pack

    def addGraphic(self, graphicItem):
        """
        Add a graphic item to the scene.

        You can pass multiple data types.
            string: Creates a text item in the scene.
            Controls/Widgets: Adds them directly to the scene.
            tuple: Creates a line.
                            If the tuple is 4 ints, it will create a line based on the following syntax.
                                (x1, y1, x2, y2)
                            If the tuple is 4 ints and a QPen, it will create a line based on the following syntax.
                                (x1, y1, x2, y2, pen)
            list: Same as a tuple but, makes a rectangle instead amd uses a QBrush instead of a QPen.

        :param graphicItem:
        :return:
        """
        if isinstance(graphicItem, QtGui.QWidget):
            return self._scene.addWidget(graphicItem)

        elif isinstance(graphicItem, str):
            return self._scene.addText(graphicItem)

        elif isinstance(graphicItem, tuple):
            if len(graphicItem) == 4:
                return self._scene.addLine(graphicItem[0], graphicItem[1], graphicItem[2], graphicItem[3])
            elif len(graphicItem) == 5:
                return self._scene.addLine(graphicItem[0], graphicItem[1], graphicItem[2], graphicItem[3],
                                           graphicItem[4])

        elif isinstance(graphicItem, list):
            if len(graphicItem) == 4:
                return self._scene.addRect(graphicItem[0], graphicItem[1], graphicItem[2], graphicItem[3])
            elif len(graphicItem) == 5:
                return self._scene.addRect(graphicItem[0], graphicItem[1], graphicItem[2], graphicItem[3],
                                           graphicItem[4])

        else:
            self._scene.addItem(graphicItem)
            return graphicItem

    def deleteAllOf(self, cls):
        """
        Delete all of a specific graphic type in the scene.
        :param cls:
        :return:
        """
        for i in self._scene.items():
            if isinstance(i, cls):
                self._scene.removeItem(i)

    def clear(self):
        """
        Clear all items from this widget.
        :return:
        """
        self._scene.clear()
