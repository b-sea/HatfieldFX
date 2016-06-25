# PySide import
from PySide import QtGui, QtCore

# utilities
from utilities import instance, applyHFXStyle

# python imports
from os.path import basename


__all__ = [
    'Application'
]


class ApplicationNavigation(QtGui.QListWidget):
    """
    Application side bar navigation
    """

    def __init__(self, application):
        """
        :param application:
        """
        super(ApplicationNavigation, self).__init__(parent=application)

        self.setSelectionMode(self.ExtendedSelection)

        applyHFXStyle(self)

        # create path map
        self._pathMap = []
        self._createdPaths = {}
        self._name = ''

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def clearPaths(self):
        self._pathMap = []

    def refresh(self):
        """
        Update the navigation list
        :return:
        """
        # init function
        self.clear()
        self._createdPaths = {}

        # loop over all paths
        for path in self._pathMap:

            # check if this is a url path
            if '/' not in path:

                # register new path
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
                            self._createdPaths[currentPath].setFlags(QtCore.Qt.NoItemFlags)

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

    def addPath(self, path, index=None):
        """
        Add a path to the navigation bar.
        :param path:
        :return:
        """
        if index:
            self._pathMap.insert(index, path)
        else:
            self._pathMap.append(path)

        # refresh the nav bar
        self.refresh()


class Application(QtGui.QMainWindow):
    """
    HFX application
        Acts as the central widget for your application.
    """

    # dock variables
    DockLeft = QtCore.Qt.LeftDockWidgetArea
    DockRight = QtCore.Qt.RightDockWidgetArea
    DockBottom = QtCore.Qt.BottomDockWidgetArea
    DockTop = QtCore.Qt.TopDockWidgetArea

    # App styles
    WebPage = 0
    SimpleDesktop = 1

    def __init__(self, name, icon=None, search=None):
        """
        :param name:
        :param style:
        :param icon:
        :param search:
        """
        # prep the application
        instance.launchPrep(self, name)

        # init application
        super(Application, self).__init__()

        applyHFXStyle(self)

        # instance variables
        self._appFuncMap = {}
        self._widgetMap = {}
        self._widgetTools = {}
        self._currentPage = None
        self._widgetBar = QtGui.QToolBar()
        self._widgetBar.setOrientation(QtCore.Qt.Vertical)

        # default widgets
        self._navBar = ApplicationNavigation(self)
        self._navBar.setName('')
        self._functionBar = ApplicationNavigation(self)
        self._functionBar.setName('Actions')
        container = QtGui.QWidget()

        # layout
        self._container = QtGui.QHBoxLayout()
        self._container.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self._container.addWidget(self._widgetBar)
        container.setLayout(self._container)

        # add widgets
        self.addSidePanel(self.DockLeft, self._navBar, lockToApp=True)
        self.addSidePanel(self.DockLeft, self._functionBar, lockToApp=True)
        self.setCentralWidget(container)

        # make connection
        self._navBar.itemClicked.connect(self.goToPage)
        self._functionBar.itemClicked.connect(self.runFunction)

        self.layout().setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

    def clearToolbar(self):
        """
        Clear the tool bar
        :return:
        """
        for tool in self._widgetTools.values():
            tool.setVisible(False)

    def addApplicationFunction(self, url, function, tip=None):
        """
        Add a function to the application.
        :param url:
        :param function:
        :param tip:
        :return:
        """
        if '/' not in url:
            action = self.menuBar().addAction(url)
        else:
            # pull function data
            functionName = url.rsplit('/', 1)[1]
            path = ''
            menu = None

            # loop through all the split url path
            for part in url.split('/'):

                # filter out empty parts
                if part == '':
                    continue

                path += '/' + part

                # create the action
                if part == functionName:
                    action = menu.addAction(functionName)
                    break

                if path in self._appFuncMap:
                    menu = self._appFuncMap[path]
                else:
                    menu = self.menuBar().addMenu(part)
                    self._appFuncMap[path] = menu

        action.triggered.connect(function)
        if tip:
            action.setToolTip(tip)

    def runFunction(self, function):
        for widget in self.currentPage():
            try:
                widget.functions()[function.url]()
            except KeyError:
                pass

    def goToPage(self, page):
        """
        Go to a page based on the pages url passed.
        :param page:
        :return:
        """
        # allow for direct string calls to the url
        if isinstance(page, (str, unicode)):
            urls = [page]
        else:
            urls = []
            for page in self._navBar.selectedItems():
                try:
                    urls.append(page.url)
                except AttributeError:
                    pass

        self._functionBar.clearPaths()
        self._functionBar.refresh()
        self.clearToolbar()

        # hide all widgets
        for widget in self._widgetMap.values():
            if widget is not None:
                widget.hide()

        self._currentPage = []

        # loop over all urls
        for url in urls:
            # hide all the existing widgets and show the one for the url provided.
            if url in self._widgetMap and self._widgetMap[url] is not None:

                # show the widget for the url provided.
                self._widgetMap[url].show()
                self._currentPage.append(self._widgetMap[url])

                if instance.isHFXWidget(self._widgetMap[url]):
                    for function in sorted(self._widgetMap[url].functions()):
                        widget = self._widgetMap[url].functions()[function]
                        if isinstance(widget, QtGui.QWidget):
                            if function not in self._widgetTools:
                                if instance.isHFXWidget(widget):
                                    action = self._widgetBar.addWidget(widget.thisWidget())
                                else:
                                    action = self._widgetBar.addWidget(widget)
                                self._widgetTools[widget] = action
                            self._widgetTools[widget].setVisible(True)
                            self._widgetTools[widget].setEnabled(True)
                        else:
                            self._functionBar.addPath(function)

                self._navBar._createdPaths[url].setSelected(True)

    def currentPage(self):
        return self._currentPage

    def addSidePanel(self, where, widget, lockToApp=False):
        """
        Add a widget to the side panel.
        :param lockToApp:
        :param where: Application.DockPosition
        :param widget:
        :return:
        """
        dock = QtGui.QDockWidget(widget.name())
        widget = instance.validateWidgetLayout(widget)
        dock.setWidget(widget)

        self.addDockWidget(where, dock)

        # set up flags
        if lockToApp:
            dock.setFeatures(dock.NoDockWidgetFeatures)
        else:
            dock.setFeatures(dock.DockWidgetMovable)

    def addWidget(self, path, widget=None, index=None):
        """
        Add a widget to this app. You need to provide a path.
            example:

            app.addWidget('/Getting Started/Welcome', WelcomeWidget())
        :param path:
        :param widget:
        :return:
        """
        # register with the nav bar
        self._navBar.addPath(path, index)

        # add to widget map
        self._widgetMap[path] = None
        if widget is not None:
            self._widgetMap[path] = instance.validateWidgetLayout(widget)
            self._container.addWidget(self._widgetMap[path])

        # go to the page
        self.goToPage(path)

    def getWidgetAt(self, url):
        """
        Grab a widget based on the url provided.
        :param url:
        :return:
        """
        return self._widgetMap[url]

    def closeAllPages(self):
        self._navBar.clearSelection()

    def show(self):
        """
        Custom show that executes the application environment if it doesnt exist.
        :return:
        """
        instance.waitTillClose(self)
