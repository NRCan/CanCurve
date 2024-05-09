#===============================================================================
# plugin metadata
#===============================================================================
__version__='0.0.2'

#===============================================================================
# plugin entry point
#===============================================================================
# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CanCurve class from file CanCurve.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .plugin import CanCurve
    return CanCurve(iface)

#===============================================================================
# dependency check
#===============================================================================

 

import importlib, warnings

def check_package(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        print(f'module {package_name} is installed')
    else:
        warnings.warn(f'module \'{package_name}\' not installed')

 
check_package('openpyxl')

