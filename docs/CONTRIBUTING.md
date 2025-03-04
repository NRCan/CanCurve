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