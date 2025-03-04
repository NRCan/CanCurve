#CanCurve documentation

CanCurve uses Sphinx and ReadTheDocs

## build sphinx documentation locally
need an environment like this:
```
  - python
  - sphinx==8.0.*
  - sphinx-rtd-theme
  - pip
  - pip:
    - sphinx-lint
```

from within this, call something like this to build:
```bat
:: change to documentation
 
cd %~dp0..\docs

:: call builder CLI
ECHO on
 
sphinx-build -M html .\source .\build --jobs=4 --verbose --show-traceback --nitpicky --warning-file=.\build\sphinx_warnings.txt -c .\source


:: launch it
call build\html\index.html
```

## update screen shots
call the `update_ui_screenshots.py` with something like this:
```
:: activate the environment
call l:\09_REPOS\04_TOOLS\CanCurve\env\activate_py.bat

:: VARIABLES
SET TEST_DIR=%SRC_DIR%\docs\update_ui_screenshots.py
SET WORKERS=8
 
:: call pytest
ECHO starting tests in separate windows
start cmd.exe /k python -m pytest --maxfail=10 %TEST_DIR% -c %SRC_DIR%\tests\pytest.ini

```