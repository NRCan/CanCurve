:: plugin deployment help

:: setup environment
call %~dp0../env/activate_py.bat

:: change to plugin directory
cd %SRC_DIR%/%PROJ_NAME%

ECHO on

::It internally calls pyrcc5 to handle the conversion of .qrc files.
:: pb_tool compile

pyrcc5 -o resources.py resources.qrc

cmd.exe /k