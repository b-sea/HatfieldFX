"""
Settings widget for modifying the HFX settings.
"""
import HFX


__all__ = [
    'Settings'
]


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
        HFX.Application.__init__(self, 'HFX Settings Panel')

        # get the HFX nav and reset it back to the top level of HFX. Then make a settings database if it doesn't exist.
        nav = HFX.HFX_NAV
        nav.backToStart()

        # connect and or create the database.
        settingsDB = nav.mkdb('settings')


Settings().show()
