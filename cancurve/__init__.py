#===============================================================================
# plugin metadata
#===============================================================================
__version__='1.2.0'

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

from packaging import version

def check_package(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        #print(f'module {package_name} is installed')
        pass
    else:
        warnings.warn(f'module \'{package_name}\' not installed')

 
check_package('openpyxl')


try:
    import pandas as pd
except ImportError:
    warnings.warn("pandas is not installed!")
else:
    required_version = "2.0.0"
    current_version = pd.__version__
    # Skeptically assert that the current pandas version meets the minimum requirement.
    assert version.parse(current_version) >= version.parse(required_version), (
        f"pandas version {current_version} is below the required {required_version}"
    )