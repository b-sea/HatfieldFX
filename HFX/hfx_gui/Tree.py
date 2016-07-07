# PySide import
from PySide import QtGui, QtCore

# utility import
from utilities import ConvertToHFX
from HFX import TransientDB, getDB, Jumper

# python imports
import sys
import xml.etree.ElementTree as et
import xml.dom.minidom as dom
from os.path import exists, splitext, join, basename
from os import listdir


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
                 multiSelection=False,
                 itemClass=None):
        """
        :param label:
        :param headers:
        :param hideHeaders:
        :param canEdit:
        :param multiSelection:
        :param itemClass:
        """
        super(Tree, self).__init__(label=label)

        # instance vars
        self._itemClass = QtGui.QTreeWidgetItem
        if itemClass:
            self._itemClass = itemClass
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

    def setHeaders(self, labels):
        """
        Pass a list of strings to define the headers.
        :param labels:
        :return:
        """
        if isinstance(labels, list):
            self.setColumnCount(len(labels))
            self.setHeaderLabels(labels)
        else:
            self.setColumnCount(1)
            self.setHeaderLabels([labels])

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
        return self.addItem(*args, parent=self.RogueItem, **kwargs)

    def addItem(self, labels, parent=None, bgColor=None, fgColor=None, widgets=None, icons=None, Class=None):
        """
        Add an item to the Tree
        :param Class: pass the class that you would like the tree widget to build the tree with
        :param labels: list of labels
        :param parent: parent item, None is default and will add the item as a top level
        :param bgColor: list of items background colors
        :param fgColor: list of items foreground colors
        :param widgets: list of widgets to add to this item
        :param icons: list of icons to add to this item
        :return:
        """
        if parent is None:
            parent = self
        else:
            pass

        if Class:
            itemClass = Class
        else:
            itemClass = self._itemClass

        if isinstance(labels, itemClass):
            if parent is None:
                parent = self
            if parent is self:
                parent.addTopLevelItem(labels)
            else:
                if isinstance(parent, itemClass):
                    parent.addChild(labels)
                else:
                    raise Exception('Invalid parent passed. ' + str(type(parent)))
            return labels

        # create item
        elif parent is None:
            item = itemClass(self)
        elif parent is self.RogueItem:
            item = itemClass()
        elif isinstance(parent, (Tree, itemClass)):
            item = itemClass(parent)
        else:
            raise Exception('Invalid parent passed. ' + str(type(parent)))

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


class DataTree(Tree):
    """
    Load a data type into this view.
        Supported types.
            XML
            JSON
            HFX TransientDB
            HFX StaticDB
    """
    def __init__(self, label=None, canEdit=False, multiSelection=False, canEditFields=False):
        super(DataTree, self).__init__(canEdit=canEdit, label=label, multiSelection=multiSelection, canEditFields=canEditFields)
        self._database = TransientDB()

    def encodeXML(self, filename=None):
        """
        Encodes the Tree to an xml.
        :type filename:
        :return: etree root element
        """
        def recurse(item, parent=None):
            tag = item.text(0)

            if tag.startswith('TEXT: '):
                parent.text = tag.replace('TEXT: ', '')
                return

            if parent is None:
                element = et.Element(tag)
            else:
                element = et.SubElement(parent, tag)

            for col in xrange(item.columnCount()):
                if col == 0:
                    continue

                value = item.text(col)
                if value == '':
                    continue

                if '=' in value:
                    element.set(value.split('=')[0], value.split('=')[1])
                else:
                    element.set(item.treeWidget().headerItems()[col], value)

            for childIndex in xrange(item.childCount()):
                recurse(item.child(childIndex), element)

        rootElement = et.Element('root')
        rootItem = self.invisibleRootItem()
        rootItem.setText(0, 'root')
        recurse(rootItem, rootElement)
        trueRoot = list(rootElement)[0]

        if filename:
            f = open(filename, 'w')
            f.write(prettify(trueRoot))
            f.close()

        print prettify(trueRoot)

        return trueRoot

    def decodeXML(self, data):
        """
        Decode XML files
        :param data:
        :return:
        """
        def recurse(element, parent=None):
            attributes = []
            for attribute in element.keys():
                attributes.append(attribute + '=' + element.get(attribute))

            item = self.addItem([element.tag] + sorted(attributes), parent=parent, fgColor=[self.green])

            if element.text is not None:
                if '\n' not in element.text:
                    self.addItem('TEXT: ' + element.text, parent=item, fgColor=[self.magenta])

            for child in element:
                recurse(child, parent=item)

        root = et.fromstring(data)
        tree = et.ElementTree(root)

        headers = ['Tags And Text']
        count = 0

        for element in tree.iter():
            if len(element.keys()) > count:
                count = len(element.keys())

        for dataField in xrange(1, count + 1):
            headers.append('Data Field ' + str(dataField))

        self.setHeaders(headers)

        recurse(root)

    def decodeJSON(self, data):
        """
        Decode JSON files
        :param data:
        :return:
        """

    def decodeHFXDB(self, path, targetTables=None):
        """
        Decode HFX databases
        :param path:
        :return:
        """
        database = Jumper(path).connectDB(basename(path))

        columnCount = 1

        for table in database.tables():
            if table == '_default':
                continue

            if targetTables:
                if table not in targetTables:
                    continue

            # add the table widget
            tableItem = self.addItem([table], fgColor=[self.green])

            # connect to the table in the database.
            table = database.table(table)

            # build item map
            itemMap = {}
            for entry in table.all():
                name = [entry.eid]
                if 'name' in entry:
                    name = [entry['name']]

                attributes = []
                for attribute in entry:
                    attributes.append(attribute + '=' + str(entry[attribute]))

                itemMap[entry.eid] = self.createItem(name)
                var = 0
                for data in name + sorted(attributes):
                    itemMap[entry.eid].setText(var, data)
                    var += 1

                if len(entry) + 1 > columnCount:
                    columnCount = len(entry) + 1

            for entry in table.all():
                if 'parent' not in entry or entry['parent'] is None:
                    self.addItem(itemMap[entry.eid], parent=tableItem)
                    continue
                itemMap[int(entry['parent'])].addChild(itemMap[entry.eid])

        headers = ['Entry']
        for dataField in xrange(1, columnCount):
            headers.append('Data Field ' + str(dataField))
        self.setHeaders(headers)

    def validateFile(self, _file):
        """
        Checks if this is a supported type. Then chooses the correct decoder.
        :param _file:
        :return:
        """
        decoders = {'.json': self.decodeJSON, '.db': self.decodeHFXDB, '.xml': self.decodeXML}

        if '.' in _file:
            ext = splitext(_file)[1]
        else:
            if getDB(_file):
                getDB(_file)
            return

        # filter out
        if ext not in decoders.keys():
            raise Exception('Not a valid file type ' + _file)

        if ext == '.db':
            decoders[ext](_file)
        else:
            decoders[ext](open(_file).read())

    def load(self, name):
        """
        Load a data file into the view.
        :param name:
        :return:
        """
        # check if this is a valid file path on the system.
        if exists(name):
            self.validateFile(name)
            return

        # loop over system paths to see if the file exists there.
        for path in sys.path:
            for _file in listdir(path):
                if _file.startswith(name):
                    self.validateFile(join(path, _file))
                    return


def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    reparsed = dom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")