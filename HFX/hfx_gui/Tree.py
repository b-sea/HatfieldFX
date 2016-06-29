# PySide import
from PySide import QtGui, QtCore

# utility import
from utilities import ConvertToHFX


class Tree(ConvertToHFX, QtGui.QTreeWidget):
    """
    Tree widget
    """

    # colors
    red = QtCore.Qt.darkRed
    green = QtCore.Qt.darkGreen
    blue = QtCore.Qt.darkBlue
    yellow = QtCore.Qt.darkYellow
    cyan = QtCore.Qt.darkCyan
    magenta = QtCore.Qt.darkMagenta

    RogueItem = 2

    def __init__(self,
                 label=None,
                 headers=None,
                 hideHeaders=False,
                 canEdit=False,
                 canEditFields=False,
                 multiSelection=False):
        """
        :param label:
        :param headers:
        :param hideHeaders:
        :param canEdit:
        :param multiSelection:
        """
        super(Tree, self).__init__(label=label)

        # instance vars
        self._items = []

        # hide headers
        self.setHeaderHidden(hideHeaders)

        # add headers
        if headers:
            self.setColumnCount(len(headers))
            self.setHeaderLabels(headers)

        # selection
        if multiSelection:
            self.setSelectionMode(self.ExtendedSelection)

        if not canEdit:
            self.setSortingEnabled(True)
        else:
            self.setDragDropMode(self.InternalMove)

        # edit fields
        if canEditFields:
            self.itemDoubleClicked.connect(self.editItem)

        # remove double click expand
        self.setExpandsOnDoubleClick(False)

        # set up context menu
        self.addContextFunction('Expand all', self.expandAll)
        self.addContextFunction('Collapse all', self.collapseAll)
        self.addContextSplit()

    def closeAllOpenEditors(self):
        """
        Closes all Persistent editors
        :return:
        """
        for _item in self.items():
            for _column in xrange(0, self.columnCount()):
                self.closePersistentEditor(_item, _column)

    def keyPressEvent(self, event):
        """
        Key press event handle
        :param event:
        :return:
        """
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            self.closeAllOpenEditors()

    def editItem(self, item, column):
        """
        Open an item to edit
        :param item:
        :param column:
        :return:
        """
        self.closeAllOpenEditors()
        self.openPersistentEditor(item, column)

    def items(self):
        """
        Get a list of all the created items
        :return:
        """
        return self._items

    def clear(self):
        """
        :return:
        """
        self._items = []
        QtGui.QTreeWidget.clear(self)

    def itemOrder(self, items=False):
        """
        Get the order of all the items in this tree
        :return:
        """
        above = self.topLevelItem(0)

        expandPast = {}
        for item in self.items():
            expandPast[item] = item.isExpanded()

        self.expandAll()

        order = []

        if items:
            order.append(above)
            while 1:
                above = self.itemBelow(above)
                if above is None:
                    break
                order.append(above)

            for item in expandPast:
                item.setExpanded(expandPast[item])

            return order

        content = []
        for col in range(0, self.columnCount()):
            content.append(str(above.text(col)))
        order.append(content)

        while 1:
            above = self.itemBelow(above)
            if above is None:
                break

            content = []
            for col in range(0, self.columnCount()):
                content.append(str(above.text(col)))

            order.append(content)

        for item in expandPast:
            item.setExpanded(expandPast[item])

        return order

    def resize(self):
        """
        Resize all columns to fit the contents
        :return:
        """
        for col in range(0, self.columnCount()):
            self.resizeColumnToContents(col)

    def sort(self, column):
        """
        Sort the tree based on a column
        :param column:
        :return:
        """
        self.sortByColumn(column, QtCore.Qt.AscendingOrder)

    def createItem(self, *args, **kwargs):
        """
        :return:
        """
        self.addItem(parent=self.RogueItem, *args, **kwargs)

    def addItem(self, labels, parent=None, bgColor=None, fgColor=None, widgets=None, icons=None):
        """
        Add an item to the Tree
        :param labels: list of labels
        :param parent: parent item, None is default and will add the item as a top level
        :param bgColor: list of items background colors
        :param fgColor: list of items foreground colors
        :param widgets: list of widgets to add to this item
        :param icon: list of icons to add to this item
        :return:
        """
        # determine parent
        if parent is self.RogueItem and not isinstance(labels, QtGui.QTreeWidgetItem):
            parent = None
        elif parent is None:
            parent = self
        else:
            pass

        if isinstance(labels, QtGui.QTreeWidgetItem):
            parent.addChild(labels)
            return

        # create item
        item = QtGui.QTreeWidgetItem(parent)

        self.setIconSize(QtCore.QSize(20, 20))

        # register new item
        self._items.append(item)

        # build item per column, more efficient
        for column in xrange(0, self.columnCount()):

            # add Icons
            try:
                if icons is not None:
                    icon = QtGui.QIcon()
                    if isinstance(icons, (str, unicode)):
                        icon.addFile(icons)
                        item.setIcon(column, icon)
                    else:
                        if icons[column] is not None:
                            icon.addFile(icons[column])
                            item.setIcon(column, icon)
            except IndexError:
                pass

            # add labels
            try:
                if isinstance(labels, (str, unicode)):
                    if column == 0:
                        item.setText(0, str(labels))
                else:
                    label = labels[column]
                    if label is None or label == '':
                        continue
                    item.setText(column, str(label))
            except IndexError:
                pass


            # add coloring
            if fgColor:
                try:
                    item.setForeground(column, fgColor[column])
                except (IndexError, TypeError):
                    pass

            if bgColor:
                try:
                    item.setBackground(column, bgColor[column])
                except (IndexError, TypeError):
                    pass


            # add widgets
            if widgets:
                try:
                    widget = widgets[column]
                    widget.setParent(self)
                    self.setItemWidget(item, column, widget)
                except (IndexError, TypeError):
                    pass

        # item resizing
        sizeHint = item.sizeHint(0)
        sizeHint.setHeight(30)
        sizeHint.setWidth(50)
        item.setSizeHint(0, sizeHint)

        # return the final item
        return item