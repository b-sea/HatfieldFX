"""
Initial load up.

This should create the HFX namespace as well as handle the gui imports and python helpers.
"""
__author__ = 'Alex Hatfield'
__version__ = '0.2.0'

HFX_APP = None

# python imports
import os
import sys

# package imports
from hfx_py import *

sysNav = Jumper(__file__)
sysNav.cd('site')
sysNav.addPathToSys()


if 'HFX_APP' in os.environ:
    HFX_APP = os.environ['HFX_APP']

if 'HFX_GUI' in os.environ.keys() or HFX_APP is None:
    """
    Execute HFX in stand alone form using PySide
    """
    print 'product: HFX'
    print 'by: HatfieldFX, LLC'
    print 'author: Alex Hatfield'
    print 'Version: ' + __version__
    print '---------------'
    print 'Python version'
    print sys.version
    print

    # HFX namespace
    from hfx_gui import *
