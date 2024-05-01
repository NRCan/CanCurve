# CanCurve development

## Installation
Typically, development should employ a virtual environment with pyqgis bindings. 
Some additional packages for testing are specified in `./requirements.txt`

### PYTHONPATH
only the source directory should be included (`./CanCurve` not `./CanCurve/cancurve`)

## Tests
pytests are in `./tests`

## Compiling
the only compiling typically requied is when the qt `resources.qrc` file is changed. This needs to be ported to a python module (typically using  `pyrcc5 -o resources.py resources.qrc` as in `./dev_tools/plug_compile.bat`)

## Deploying Plugin

### Active Development
Typically a `dev` QGIS profile is maintained with a custom `QGIS_PLUGINPATH` pointed to the project source directory. This facilitates plugin updating with the `plugin reload` (ie no real deployment) 

### Pre-Release testing
Pre-release testing (and full deployment) employ a zip of the plugin directory (see `./dev_tools/plug_zip.bat`):
1) remove all `__pychace__`
2) zip/archive the plugin directory

This zip file can then be distributed using a git-hub release (upload the zip file to the release)

### Full QGIS Repository release
1) create the plugin zip as above
