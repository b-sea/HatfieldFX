"""
Pure python helpers
"""

# python imports
import subprocess


def python(pathToFile):
    """
    Launch an app or file with python.
    :param pathToFile:
    :return:
    """
    arg = ['python', pathToFile]
    subprocess.Popen(arg)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]