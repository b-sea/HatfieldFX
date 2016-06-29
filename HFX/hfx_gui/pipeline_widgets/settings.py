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
        self._applicaitons = self._settingsDB.table('Applications')
        self._applicaitons.all()

        # context functions
        self.addContextFunction('New Application Environment', self.addApplication)

    def addApplication(self):
        """
        Create a new application.
        :return:
        """
        self._applicaitons.insert({'envs': [], 'paths': [], 'type': 'application', 'name': 'Unnamed', 'parent': None})


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


Settings().show()
