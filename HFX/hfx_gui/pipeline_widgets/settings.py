"""
Settings widget for modifying the HFX settings.
"""
# HFX imports
import HFX

# python imports
import os
import sys


__all__ = [
    'Settings'
]


class Applications(HFX.Tree):
    """
    Application tree for selecting/creating new application environments.
    """
    def __init__(self):
        """
        :return:
        """
        super(Applications, self).__init__('Application Environments', hideHeaders=True)

        # grab the settings.db
        self._settingsDB = HFX.getDB('settings')
        self._applications = self._settingsDB.table('Applications')

        # context functions
        self.addContextFunction('New Application Environment', self.addApplication)
        self.addContextFunction('Refresh', self.refresh)

        self.refresh()

    def refresh(self):
        """
        refresh the app list.
        :return:
        """
        self.clear()
        apps = self._settingsDB.findAll('type', '==', 'application', table='Applications')

        itemMap = {}
        for app in apps:
            itemMap[app.eid] = self.createItem(app['name'])

        for app in apps:
            parent = app['parent']
            if parent is None:
                item = self.addItem(itemMap[app.eid])
            else:
                item = self.addItem(itemMap[app.eid], parent=itemMap[int(parent)])

            item.appID = app.eid


    def addApplication(self):
        """
        Create a new application.
        :return:
        """
        # set the default values
        applicationPathDefault = ''
        parent = None

        selection = self.selectedItems()
        if selection:
            parentApp = selection[0].text(0)
            search = self._settingsDB.findExactly('name', '==', parentApp, table='Applications')
            if search:
                applicationPathDefault = search['launch']
                parent = str(search.eid)

        applicationName = HFX.LineEdit('Application Name')
        applicationPath = HFX.FileLineEdit('Application Path')
        applicationPath.setValue(applicationPathDefault)

        dialog = HFX.Dialog('Create Application')
        dialog.addWidget(applicationName)
        dialog.addWidget(applicationPath)
        if not dialog.show():
            return

        self._applications.insert({
            'envs': [],
            'paths': [],
            'type': 'application',
            'name': applicationName.value(),
            'parent': parent,
            'launch': applicationPath.value()
        })

        self.refresh()


class Settings(HFX.Application):
    """
    Settings widget panel for managing the settings for HFX. This includes building application environments and setting
    up launchers.
    """

    def __init__(self):
        """
        Launches the settings widget for HFX.
        :return:
        """
        HFX.Application.__init__(self, '')

        # get the HFX nav and reset it back to the top level of HFX. Then make a settings database if it doesn't exist.
        nav = HFX.HFX_NAV
        nav.backToStart()

        # connect and or create the database.
        self._settingsDB = nav.mkdb('settings')
        self._applications = self._settingsDB.table('Applications')
        self._paths = self._settingsDB.table('Paths')
        self._vars = self._settingsDB.table('Vars')

        # build ui
        self._apps = Applications()
        self._sysPath = HFX.List('sys.path Management', cascading=False, numbered=True)
        self._envVariables = HFX.Tree('Environment Variables', headers=['Variable', 'Value'])

        # add the widgets
        self.addWidget('/Application Info/Paths', self._sysPath)
        self.addWidget('/Application Info/Environment', self._envVariables)
        self.addSidePanel(self.DockRight, self._apps)

        # load the default python env
        self.loadPythonEnv()

        # make connections
        self._apps.connectTo(self._apps.itemClicked, self.loadAppData)

    def loadPythonEnv(self):
        """
        This just loads pythons sys path information and environment variables.
        :return:
        """
        # loop through sys paths
        self._sysPath.addPaths(sys.path)

        # loop through env
        for var in sorted(os.environ.keys()):
            self._envVariables.addItem([var, os.environ[var]])

    def loadAppData(self, item):
        """
        Load the selected Applications data.
        :param item:
        :return:
        """
        print self._applications.get(eid=item.appID)


Settings().show()

