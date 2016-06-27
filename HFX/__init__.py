"""
Initial load up.

This should create the HFX namespace as well as handle the gui imports and python helpers.
"""
__author__ = 'Alex Hatfield'
__version__ = '0.3.0'

# package imports
from hfx_py import *

# python imports
import sys
import logging

logging.basicConfig()

# establish navigation jumper.
HFX_NAV = Jumper(__file__)
HFX_NAV.cd('site')
HFX_NAV.addPathToSys()
HFX_NAV.backToStart()

# product information
logging.info('product: HFX')
logging.info('by: HatfieldFX, LLC')
logging.info('author: Alex Hatfield')
logging.info('Version: ' + __version__)

# python information
logging.info('Python version')
for line in sys.version.split('\n'):
    logging.info(line)

# gui tools
try:
    # HFX namespace
    from hfx_gui import *
    guiKitVersion()
except ImportError, e:
    logging.warning('Cant load HFX gui tools.')
    logging.error('\t' + str(e))