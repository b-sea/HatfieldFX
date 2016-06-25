
# python imports
import sys

# package imports
from hfx_py import *
from package_utils import *

__version__ = '0.2.0'

HFX_APP = None

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
    from gui import *
    import hfx_gui

if HFX_APP is not None:
    loadPipeline(HFX_APP)