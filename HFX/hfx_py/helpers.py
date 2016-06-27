"""
Pure python helpers

Meant to help with python interaction.
"""

# python imports
import subprocess


__all__ = [
    'python',
    'Singleton'
]


def python(pathToFile):
    """
    Launch an app or file with python.
    :param pathToFile:
    :return:
    """
    arg = ['python', pathToFile]
    subprocess.Popen(arg)


class Singleton(type):

    singles = {}

    def __call__(cls, *args, **kwargs):
        """
        Override for new instances.
        :param name:
        :param parents:
        :param dct:
        :return:
        """
        if cls not in cls.singles:
            cls.singles[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls.singles[cls]
