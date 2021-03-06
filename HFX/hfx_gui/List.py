# PySide import
from PySide import QtGui, QtCore

# utility imports
from utilities import ConvertToHFX

# Python imports
from os.path import basename


class List(ConvertToHFX, QtGui.QListWidget):
    """
    List widget
    """

    def __init__(self,
                 label=None,
                 canEdit=False,
                 multiSelection=False,
                 cascading=True,
                 numbered=False):
        """
        """
        super(List, self).__init__(label=label)

        # create path map
        self._dataMap = {}
        self._pathMap = []
        self._createdPaths = {}
        self._cascading = cascading
        self._numbered = numbered

        # selection
        if multiSelection:
            self.setSelectionMode(self.ExtendedSelection)

        if canEdit:
            self.setDragDropMode(self.InternalMove)

    def items(self):
        """
        Get a list of all items.
        :return:
        """

        row = 0
        allItems = []

        while 1:
            item = self.item(row)
            if item is None:
                return allItems

            try:
                item.url
            except AttributeError:
                continue

            allItems.append(item)

            row += 1

    def value(self):
        value = []
        for item in self.selectedItems():
            digitDetect = item.text().split('\t')[0]
            digitDetect.isDigit()
            t = item.text().replace(digitDetect, '')
            value.append(str(t).strip())
        return value

    def selectItem(self, url):
        for item in self.items():
            try:
                if url == item.url:
                    item.setSelected(True)
                    return
            except AttributeError:
                pass

    def selectItems(self, urls):
        for item in self.items():
            try:
                if item.url in urls:
                    item.setSelected(True)
            except AttributeError:
                pass

    def clearPaths(self):
        self._dataMap = {}
        self._pathMap = []
        self.refresh()

    def refresh(self):
        """
        Update the navigation list
        :return:
        """
        # init function
        self.clear()
        self._createdPaths = {}
        num = 1

        # loop over all paths
        for path in self._pathMap:

            # check if this is a url path
            if '/' not in path or not self._cascading:

                # register new path
                if self._numbered:
                    self._createdPaths[path] = QtGui.QListWidgetItem(str(num) + '\t' + path)
                else:
                    self._createdPaths[path] = QtGui.QListWidgetItem(path)

                # create the item
                self.addItem(self._createdPaths[path])

                # resize the item
                sizeHint = self._createdPaths[path].sizeHint()
                sizeHint.setHeight(30)
                self._createdPaths[path].setSizeHint(sizeHint)

                # add data
                self._createdPaths[path].url = path

            else:
                # loop vars
                indent = ''
                currentPath = ''
                base = basename(path)

                # loop over all parts of the url style path
                for part in path.split('/'):

                    # skip this loop if the part is empty
                    if part == '':
                        continue

                    # check if this path has already been created.
                    currentPath += '/' + part
                    if currentPath not in self._createdPaths:

                        # create the item and check the flags
                        self._createdPaths[currentPath] = QtGui.QListWidgetItem(indent + part)

                        # set the item flags
                        if part != base:
                            self._createdPaths[currentPath] = QtGui.QListWidgetItem('\t' + indent + part)
                            self._createdPaths[currentPath].setFlags(QtCore.Qt.NoItemFlags)
                        else:
                            self._createdPaths[currentPath] = QtGui.QListWidgetItem(str(num) + '\t' + indent + part)

                        # add the item
                        self.addItem(self._createdPaths[currentPath])

                        # resize the item
                        sizeHint = self._createdPaths[currentPath].sizeHint()
                        sizeHint.setHeight(30)
                        self._createdPaths[currentPath].setSizeHint(sizeHint)

                        # add data
                        self._createdPaths[currentPath].url = currentPath

                    # inc indent
                    indent += '    '

            num += 1

    def getData(self, url):
        """
        Grab the data from a url
        :param url:
        :return:
        """
        return self._dataMap[url]

    def setData(self, url, data):
        """
        Set the data of a url
        :param url:
        :param data:
        :return:
        """
        self._dataMap[url] = data

    def addPaths(self, listOfPaths):
        """
        Add a list of paths
        :param listOfPaths:
        :return:
        """
        for path in listOfPaths:
            self._pathMap.append(path)
            self._dataMap[path] = None

        self.refresh()

    def addPath(self, path, index=None, data=None):
        """
        Add a path to the navigation bar.
        :param path:
        :return:
        """
        if index:
            self._pathMap.insert(path, index)
        else:
            self._pathMap.append(path)

        self._dataMap[path] = data

        # refresh the nav bar
        self.refresh()