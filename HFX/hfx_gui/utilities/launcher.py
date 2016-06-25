
# HFX imports
import HFX

# python imports
from os.path import dirname, join


class Launcher(HFX.Application):
    """
    Default launcher for the HFX environment manager.
    """
    def __init__(self):
        """
        :return:
        """
        super(Launcher, self).__init__('HFX Launcher')

        launcher = HFX.LaunchWidget()
        launcher.appBox.addFunction('HFX Settings', self.launchSettings)

        self.setMainWidget(launcher)

        self.setMinimumWidth(250)

    def launchSettings(self):
        HFX.python(join(dirname(__file__), 'settings.py'))


def launch():
    Launcher().show()


if __name__ == '__main__':
    launch()
