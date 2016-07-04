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
        super(Applications, self).__init__('Application Environments', hideHeaders=True, multiSelection=True)

        # grab the settings.db
        self._settingsDB = HFX.getDB('settings')
        self._applications = self._settingsDB.table('Applications')

        # context functions
        self.addFunction('+', self.addApplication)
        self.addContextFunction('New Application Environment', self.addApplication)

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
        self._envVariables = HFX.DataTree('Environment Variables')

        # add functions
        self._sysPath.addFunction('Add Path', self.addSysPath)
        self._sysPath.addFunction('Remove Path', self.removeSysPath)

        # add the widgets
        self.addWidget('/Application Info/Paths', self._sysPath)
        self.addWidget('/Application Info/Environment', self._envVariables)
        self.addSidePanel(self.DockRight, self._apps)

        # make connections
        self._apps.connectTo(self._apps.itemClicked, self.loadAppData)

    def _refresh(self):
        """
        --private--
        :return:
        """

    def removeSysPath(self):
        """
        Delete a system path from the database.
        :return:
        """
        dialog = HFX.Decision('Are you sure you want to remove this path? This may effect some application environments.')

        if not dialog.show():
            print 'asdfs'
            return

    def addSysPath(self):
        """
        Register a system path.
        :return:
        """
        pathField = HFX.FileLineEdit('Directory to add')
        pathBox = HFX.CheckBox('Add to PATH as well?')
        state = HFX.OptionBox('State')
        state.addItems(['Active', 'Auto-Import', 'Disable'])

        dialog = HFX.Dialog('Add python sys path')
        dialog.addWidget(state)
        dialog.addWidget(pathBox)
        dialog.addWidget(pathField)

        if not dialog.show():
            return

        self._paths.insert(
            {
                'path': pathField.value(),
                'status': state.value(),
                'addToPath': pathBox.value()
            }
        )


    def loadAppData(self, item):
        """
        Load the selected Applications data.
        :param item:
        :return:
        """
        print self._applications.get(eid=item.appID)


Settings().show()

