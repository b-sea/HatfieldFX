
# HFX import
import HFX

#python imports
import shutil
import json
import os


EXCLUDED_SOURCES = [
    'envs',
    'type',
    'status'
]

BUILD = r'R:\pipeline\facility\software\library\builds'
APPLICATION_TEMPLATES = r'R:\pipeline\facility\software\library\application_templates'


class SettingsPanel(HFX.Application):
    """
    Settings panel for controlling the load up environment for HFX.
    """
    def __init__(self):
        """
        :return:
        """
        super(SettingsPanel, self).__init__('HFX settings', searchBar=True)

        # open pipeline
        self.environmentData = {}
        self._pipeline_data = {}
        self._current_row = 1

        # add tree widgets
        self.applications = HFX.TreeWidget('Application Environments', headers=['Application'], searchable=True)
        self.startUp = HFX.TreeWidget('Launch Config', headers=['Sources', 'State'], searchable=True)
        self.environmentSetup = HFX.TableWidget('Variables')

        # add widgets
        envPanel = HFX.Widget()
        self.addPanel(self.applications, self.DockLeft)
        self.addPanel(envPanel, self.DockLeft)

        tab = HFX.Tab()
        tab.newTab('Launch Config', self.startUp)
        tab.newTab('Environment', self.environmentSetup)

        self.setMainWidget(tab)

        # build env form panel
        self.appName = HFX.ShortTextInput('App')
        self.appArgs = HFX.ShortTextInput('Args')
        self.appPath = HFX.ShortTextInput('Path')
        self.appGui = HFX.Toggle('Use HFX Gui')

        # envPanel
        envPanel.addControl(self.appName)
        envPanel.addControl(self.appArgs)
        envPanel.addControl(self.appPath)
        envPanel.addControl(self.appGui)

        # assign functions
        self.addFunction('File', 'Save', self.commitChanges)
        self.addFunction('Build', 'Launcher', self.buildLauncher)

        self.applications.addFunction('+', self.newEnv, 'Add a new application environment.')
        self.applications.addFunction('-', self.removeEnv, 'Remove an application environment.')

        self.startUp.addFunction('+', self.addSource, 'Add a new source file or location.')
        self.startUp.addFunction('-', self.removeSource, 'Remove a source file or location.')

        self.environmentSetup.addFunction('+', self.addVariable)
        self.environmentSetup.addFunction('-', self.removeVariable)

        # make connections
        self.applications.connect(self.loadEnv)

        # init functions
        self._load()

        if 'HFX_APP' in os.environ:
            self.loadEnv(os.environ['HFX_APP'])

    def _load(self):
        self.applications.clear()
        self.startUp.clear()

        pipelines = {}

        for f in os.listdir(HFX.environmentDirectory()):
            if f.endswith('.env'):
                self.applications.addItem(f)

            elif f.endswith('.pipeline'):
                pipelines[json.load(open(os.path.join(HFX.environmentDirectory(), f)))['app']] = f

        for app in pipelines:
            self.applications.addItem(pipelines[app], parent=self.applications.findItem(app + '.env'))

        self.applications.resize()
        self.applications.expandAll()
        self.startUp.resize()

    def _loadSources(self):
        self.startUp.clear()
        for i in self._pipeline_data:
            state = HFX.OptionBox('', ['Disabled', 'Append', 'Auto-Import'], width=85)
            state.setValue(self._pipeline_data[i])
            self.startUp.addItem(str(i), widgets=[None, state])

        self.startUp.resize()

    def _writeData(self, appName, data, pipeline=None):
        suffix = '.env'
        if pipeline:
            suffix = '.pipeline'

        environmentFile = open(os.path.join(HFX.environmentDirectory(), appName + suffix), 'w')
        prettyJson = json.dumps(data, indent=4, separators=(',', ':'), sort_keys=True)
        environmentFile.write(prettyJson)
        environmentFile.close()

    def _buildLauncher(self, appName, appTemplate, buildTo=None):
        """
        Build a launcher from a template.
        :param appName:
        :param appTemplate:
        :param buildTo:
        :return:
        """
        if buildTo is None:
            buildTo = BUILD

        # confirm
        if HFX.Dialog('Would you like to build the template launcher?', ask=True).show():

            # select template
            appTemplate = os.path.join(APPLICATION_TEMPLATES, appTemplate)

            # store the files so we can build the bat file
            possibleLaunchPoints = {}

            # walk and build launcher in the target directory
            for root, dirs, files in os.walk(appTemplate):

                # replace root with build directory and any wild card replacement.
                # Create the directory if it doesnt exist.
                destRoot = root.replace(appTemplate, buildTo).replace('{APP}', appName)
                if not os.path.exists(destRoot):
                    os.makedirs(destRoot)

                # copy files and replace wild cards in filename as well as in contents.
                for f in files:

                    # build destination build bath
                    destFilename = f.replace(appTemplate, buildTo).replace('{APP}', appName)
                    destPath = os.path.join(destRoot, destFilename)

                    # append the file so we can ask about creating command files after we are done
                    possibleLaunchPoints[destFilename] = destPath

                    # copy files and replace contents
                    shutil.copy(os.path.join(root, f), destPath)
                    contents = open(destPath, 'r').read()
                    open(destPath, 'w').write(contents.replace('{APP}', appName))

            dialog = HFX.Dialog('Would you like to pick the launch point?')
            points = HFX.ListWidget('Launch Points')
            points.addItems(possibleLaunchPoints.keys())
            dialog.addControl(points)

            if dialog.show():
                return str(possibleLaunchPoints[points.value()[0]])

    def _loadVariables(self):
        self.environmentSetup.clear()
        if 'env' not in self.environmentData:
            self.environmentData['env'] = {}

        self._current_row = 1
        for var in sorted(self.environmentData['env']):
            self.environmentSetup.addItem(var, self._current_row, 1)
            self.environmentSetup.addItem(self.environmentData['env'][var], self._current_row, 2)
            self._current_row += 1

    def commitChanges(self):
        """
        Commit the source list for the application environment.
        :return:
        """
        pipeline = {}
        for item in self.startUp.items():
            pipeline[item.text(0)] = self.startUp.getWidget(item, 1).value()
        self.environmentData['pipeline'] = pipeline
        self.environmentData['HFX_APP'] = self.appName.value()
        self.environmentData['HFX_APP_ARGS'] = self.appArgs.value()
        self.environmentData['HFX_APP_PATH'] = self.appPath.value()
        self.environmentData['HFX_GUI'] = self.appGui.value()

        variables = self.environmentSetup.value(how=self.environmentSetup.Rows)
        vars = {}
        if variables != {}:
            for row in variables:
                vars[str(variables[row][0].text())] = str(variables[row][1].text())

        self.environmentData['env'] = vars
        self._writeData(self.environmentData['HFX_APP'], self.environmentData)

    def createProject(self):
        """
        Create a new project.
        """
        # Build input dialog
        dialog = HFX.Dialog('Name project')
        projectName = HFX.ShortTextInput('Name')
        dialog.addControl(projectName)

        # execute dialog
        if not dialog.show():
            return

        self.pipeline.addItem(projectName.value())

    def buildLauncher(self):
        """
        Build a launcher from a template.
        """
        # build dialog
        dialog = HFX.Dialog('New HFX application environment')

        buildTo = HFX.ShortTextInput('Build to')
        buildTo.setValue(BUILD)
        template = HFX.ListWidget('Launch Template')
        template.addItems(os.listdir(APPLICATION_TEMPLATES))

        dialog.addControl(template)
        dialog.addControl(buildTo)

        if dialog.show():
            if not self.applications.value(items=True):
                HFX.Notification('You need to select an application to build launcher.').show()
                return
            targetApp = str(self.applications.value(items=True)[0].text(0).split('.')[0])
            self._buildLauncher(targetApp, str(template.value()[0]), buildTo.value())

    def newEnv(self):
        """
        Add a new env to HFX
        :return:
        """
        # build dialog
        dialog = HFX.Dialog('New HFX application environment')

        appName = HFX.ShortTextInput('Name')
        buildTo = HFX.ShortTextInput('Build to')
        buildTo.setValue(BUILD)
        template = HFX.ListWidget('Launch Template')
        template.addItems(os.listdir(APPLICATION_TEMPLATES))

        dialog.addControl(appName)
        dialog.addControl(template)
        dialog.addControl(buildTo)

        # execute dialog and bail if not accepted
        if not dialog.show():
            return

        environmentData = {
            "HFX_APP": appName.value(),
            "HFX_APP_ARGS": "",
            "HFX_APP_PATH": os.path.join(BUILD, appName.value()),
            "HFX_GUI": True,
            "pipeline": {}
        }

        if template.value():
            launchPoint = self._buildLauncher(appName.value(), str(template.value()[0]), buildTo.value())
            if launchPoint:
                environmentData["HFX_APP_PATH"] = launchPoint

        self._writeData(appName=appName.value(), data=environmentData)
        self._load()

    def removeEnv(self):
        """
        Remove an env from the HFX env list.
        :return:
        """
        if HFX.Dialog('Are you sure you want to delete the selected env(s)?').show():
            for env in self.applications.value():
                os.remove(os.path.join(HFX.environmentDirectory(), env))
            self._load()

    def addSource(self):
        """
        Add a source to the application source list
        :return:
        """
        if HFX.Dialog('Would you like to use HFX path expressions?', ask=True).show():
            dialog = HFX.Dialog('Path expression')
            path = HFX.ShortTextInput('Expression')
            dialog.addControl(path)
            if not dialog.show():
                return
            filePath = path.value()
        else:
            filePath = HFX.getDirectory()
            if not filePath:
                return

        self._pipeline_data[filePath] = 'Disabled'
        self._loadSources()

    def removeSource(self):
        """
        Add a source to the application source list
        :return:
        """
        if HFX.Dialog('Are you sure you want to delete the selected sources?').show():
            selection = self.startUp.value()
            for source in selection:
                del self._pipeline_data[source]

        self._loadSources()

    def loadEnv(self, app=None):
        """
        Load the pipeline from the env file on disk
        :return:
        """
        self.startUp.clear()
        app = self.applications.value().keys()[0]

        if app.endswith('.pipeline'):
            app = self.applications.findItem(app).parent().text(0)

        with open(os.path.join(HFX.environmentDirectory(), app)) as environment_file:
            self.environmentData = json.load(environment_file)

            # extract pipeline data
            self._pipeline_data = self.environmentData['pipeline']

            self.appName.setValue(self.environmentData['HFX_APP'])
            self.appArgs.setValue(self.environmentData['HFX_APP_ARGS'])
            self.appPath.setValue(self.environmentData['HFX_APP_PATH'])
            self.appGui.setValue(self.environmentData['HFX_GUI'])

        self._loadSources()
        self._loadVariables()

    def addVariable(self):
        """
        Add an environment variable to the application.
        """
        self.environmentSetup.addItem('newVar', self._current_row, 1)
        self.environmentSetup.addItem('newVar val', self._current_row, 2)

        self._current_row += 1

    def removeVariable(self):
        self.environmentSetup.deleteRow()
        self._current_row -= 1


def modifySettings():
    SettingsPanel().show()


if __name__ == '__main__':
    modifySettings()
