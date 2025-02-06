'''
Created on Jan. 24, 2025

@author: cef

general project-wide tests
'''
import pkg_resources, os
import pytest
from .conftest import base_dir


#===============================================================================
# HERLPERS-----
#===============================================================================
def parse_requirements(file_path):
    """
    Parse a requirements.txt file and return a dictionary
    of package names and their required versions.
    """
    requirements = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip comments and empty lines
                continue

            # Handle dependencies with specific versions or URLs
            if '@' in line or '://' in line:
                continue #skipping these
                #===============================================================
                # parts = line.split('@', 1)
                # package = parts[0].split('==')[0].strip()
                # requirements[package] = line
                #===============================================================
            elif '==' in line:
                package, version = line.split('==', 1)
                requirements[package.strip()] = version.strip()
            else:
                package = line.strip()
                requirements[package] = None  # No specific version specified
    return requirements

#===============================================================================
# TESTS--------
#===============================================================================

def test_qgis_version(qgis_app, qgis_iface):

    expected_version_int = 33414  # Version 3.34.14
    from qgis.core import Qgis
    actual_version_int = Qgis.QGIS_VERSION_INT
    assert actual_version_int == expected_version_int, f"Expected QGIS version {expected_version_int}, but got {actual_version_int}"
    
    





@pytest.mark.parametrize('requirements_path',[r'cancurve\requirements.txt'])
def test_requirements(requirements_path):
    """
    Compare the current environment's installed packages to the requirements.txt file.
    
    to generate a new file:
        pip freeze > requirements.txt
    """
    requirements_path = os.path.join(base_dir, requirements_path)
    required_packages = parse_requirements(requirements_path)

    for package, required_version in required_packages.items():
        try:
            # Get the installed version of the package
            installed_version = pkg_resources.get_distribution(package).version

            if required_version and '://' not in required_version and '@' not in required_version:
                assert installed_version == required_version, (
                    f"Package {package} has version {installed_version}, "
                    f"but {required_version} is required."
                )
        except pkg_resources.DistributionNotFound:
            pytest.fail(f"Package {package} is not installed.")
