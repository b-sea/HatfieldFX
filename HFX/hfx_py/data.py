"""
Data interacts with the existing HFX database.

Back end is tinydb
"""
# pure python db.
import tinydb

# python imports
from os.path import basename
from tempfile import NamedTemporaryFile


__all__ = [
    'StaticDB',
    'TransientDB',
    'getDB',
    'getAll'
]


# global databases.
DATABASES = {}


class _db(tinydb.TinyDB):
    """
    --private--
    """
    def __init__(self, name, location):
        """
        Load or create a db at the location in question.
        :param location:
        :return:
        """
        super(_db, self).__init__(location)

        self._name = name

        # register the database
        global DATABASES
        DATABASES[name] = self

    def __del__(self):
        try:
            global DATABASES
            del DATABASES[self.name()]
        except:
            pass

    def findAll(self, field, condition, value, table=None):
        """
        Find all data elements that match the value of the field that is evaluated with the condition. You can pass an
        optional table to search in.
        :param field:
        :param condition:
        :param value:
        :param table: optional
        :return:
        """
        result = []
        SEARCHER = self.field()

        value = str(value)
        if not value.isdigit():
            value = "'%s'" % value

        if table:
            exec "result = self.table('%s').search(SEARCHER.%s %s %s)" % (table, field, condition, value)
        else:
            exec "result = self.search(SEARCHER.%s %s %s)" % (field, condition, value)

        return result

    def findExactly(self, field, condition, value, table=None):
        """
        Find all data elements that match the value of the field that is evaluated with the condition. You can pass an
        optional table to search in.
        :param field:
        :param condition:
        :param value:
        :param table: optional
        :return:
        """
        try:
            return self.findAll(field, condition, value, table)[0]
        except IndexError:
            return None

    @staticmethod
    def field():
        """
        Create a query.
        :return:
        """
        return tinydb.Query()

    def name(self):
        """
        get the name of this database.
        :return:
        """
        return self._name


class StaticDB(_db):
    """
    This creates a database that is saved to a location on disk.
    """
    def __init__(self, name, location):
        """
        Create a fixed database at the provided location.
        :param location:
        :return:
        """
        # correct location name
        if not name.endswith('.db'):
            name += '.db'

        super(StaticDB, self).__init__(name, location + '/' + name)


class TransientDB(_db):
    """
    This creates a database that is removed after use.
    """
    def __init__(self, name=None):
        """
        Create a transient db that is destroyed after use.
        :return:
        """
        # create the temp db
        self._f = NamedTemporaryFile(suffix='.db')

        if not name:
            name = basename(self._f.name).split('.')[0]

        # super
        super(TransientDB, self).__init__(name, self._f.name)

    def __del__(self):
        self._f.close()
        _db.__del__(self)


def getDB(name):
    """
    Get a db by its name.
    :param name:
    :return:
    """
    # correct name
    if not name.endswith('.db'):
        name += '.db'
    return DATABASES[name]


def getAll():
    """
    Get a list of all current dbs
    :return:
    """
    return sorted(DATABASES.keys())

