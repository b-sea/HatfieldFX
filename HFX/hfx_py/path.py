"""
Convenience functions for system directory navigation.
"""

# python imports
import os
import sys

# package imports
import data


__all__ = [
    'Jumper'
]


class Jumper(object):
    """
    Jumper allows for quick navigation around the system. Similar to using the terminal or command prompt.
    """

    TransientDB = data.TransientDB
    StaticDB = data.StaticDB

    def __init__(self, path):
        """
        Pass the starting point path.
        :param path:
        :return:
        """

        # filter out file on init
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        # set instance variables
        self._startingPoint = path
        self._currentPath = path

    def mkdb(self, name, db=StaticDB):
        """
        Create a db at this location. By default this will create a Static DB. You can create a temp Transient DB
        instead. This will be created in the temp directory instead.
        :param name:
        :param db:
        :return:
        """
        if isinstance(db, self.TransientDB):
            return data.TransientDB(name)
        else:
            return data.StaticDB(name, self.cwd())

    def cd(self, directory):
        """
        Change to a directory.
        :param directory:
        :return:
        """
        if os.path.isdir(os.path.join(self.cwd(), directory)):
            self._currentPath = os.path.join(self.cwd(), directory)
        else:
            print 'The path you\'re trying to change to is not a directory.\n\t' + os.path.join(self.cwd(), directory)

    def up(self):
        """
        Go up a directory.
        :return:
        """
        self._currentPath = os.path.dirname(self.cwd())

    def jumpTo(self, path):
        """
        Jump to a directory. Its usually better to make a new jumper, but you can do this.
        :param path:
        :return:
        """
        if os.path.isdir(path):
            self._startingPoint = path
        else:
            print 'The path you\'re trying to jump to is not a directory.\n\t' + path

    def backToStart(self):
        """
        This will revert you back to your initial path.
        :return:
        """
        self._currentPath = self._startingPoint

    def cwd(self):
        """
        Get the current working directory.
        :return:
        """
        return self._currentPath

    def open(self, file):
        """
        Open a in the current working directory file.
        :param file:
        :return:
        """
        return open(os.path.join(self.cwd(), file))

    def addPathToSys(self, path=None):
        """
        Optional argument to add a path to the sys path. If no path is added, the current working directory is added.
        :param path:
        :return:
        """
        if path:
            path = path.replace('\\', '/')
            if not os.path.exists(path):
                print 'The path you\'re trying to add to the sys path doesn\'t exist.\n\t' + path
                return

            if not os.path.isdir(path):
                print 'The path you\'re trying to add to the sys path is a file.\n\t' + path
                return

            sys.path.append(path)

        else:
            sys.path.append(self.cwd())
