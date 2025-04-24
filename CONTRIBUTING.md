# CanCurve development
guidelines/instructions for contributing to the CanCurve project.

For contributing to the documentation, see `./docs/contributing.MD`

For development tools, see `l:\09_REPOS\01_COMMON\building_projects\pyqgis`

## Installation
Typically, development should employ a virtual environment with pyqgis bindings.
To build this requires:
- 1) pyqgis bindings (see `./readme.md` for target version)
- 2) Some additional packages used for testing and deployment are specified in `./requirements.txt`
- 3) a `./definitions.py` file is needed for some of the testing data (see below for template)

### PYTHONPATH
only the source directory should be included (`./CanCurve` not `./CanCurve/cancurve`)


### definitions.py

```python
#machine specific external filepaths
#See Shared Drive/02_proj/2403_CanCurve/10_IO to download
#https://drive.google.com/drive/folders/1Z0d40SdXU0bcI0l7CLO2aT6gYGhSu3cQ?usp=drive_link

#directory where test data is stored
test_data_dir = r's:\02_proj\2403_CanCurve\10_IO\test_data'

#directory with DDFP data from David (for comparison)
ddfp_data_dir = r's:\02_proj\2403_CanCurve\10_IO\DDF_data'
```

## Tests
pytests are in `./tests`

## Compiling
the only compiling typically required is when the qt `resources.qrc` file is changed. This needs to be ported to a python module (typically using  `pyrcc5 -o resources.py resources.qrc` as in `pyrcc5_compile.bat`)



## Deploying Plugin

### Active Development
Typically a `dev` QGIS profile is maintained with a custom `QGIS_PLUGINPATH` pointed to the project source directory. This facilitates plugin updating with the `plugin reload` (ie no real deployment).
see `l:\06_SOFT\QGIS\plugin_launchers\canCurve_QGIS_LTR_project_dev.bat`

### Pre-Release testing
Pre-release testing (and full deployment) employs a zip of the plugin directory (see `plug_zip.bat`):
1) remove all `__pychace__`
2) zip/archive the plugin directory

This zip file can then be distributed using a git-hub release (upload the zip file to the github release... NOT the git repo tracking)


### Full QGIS Repository release
- [ ] create the plugin zip as above
- [ ] in git-hub, create a new release tag (e.g., v1.2.0), summarize new features for developers. upload the zip file. 

- [ ] login to [plugins.qgis.org](https://plugins.qgis.org/accounts/login/?next=/plugins/my) using the CanFlood credentials (ask Nicky). Navigate to **Upload a plugin** and select the zip file.

- [ ] In QGIS, refresh the repository and ensure that the new version is available (may take ~10mins for the version to be available). Upgrade and check that it works.

- [ ] notify project team

## Developing an Update

the dev branch is where new features and fixes are collected and tested before release. The following should be executed on the dev branch in preparation for pushing to the main branch:

- [ ] add/update documentation where applicable
- [ ] backwards merge master into dev to capture any upstream changes (these should be minor and limited to documentation tweaks as all development is done on the dev branch). NOTE: if the main has a squash commit, you'll see some major differences.. however.. when these are actually  merged you should see only the changes. 
- [ ] ensure the version tag is updated on `.\cancurve\__init__.py`
- [ ] update the README.md to summarize any new features for users
- [ ] similarly update `.\cancurve\metadata.txt`
- [ ] execute all tests. investigate warnings. fix errors. 
- [ ] perform a 'person test' by having a non-developer follow relevant tutorials. investigate warnings and fix errors.
- [ ] Once these tests are complete **and passing**, a pull request should be completed and the dev branch merged into the main.
- [ ] Follow the above **Deploying Plugin/Full QGIS Repository Release** on the main branch 