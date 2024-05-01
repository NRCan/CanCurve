
__version__='0.0'

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CanCurve class from file CanCurve.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .plugin import CanCurve
    return CanCurve(iface)