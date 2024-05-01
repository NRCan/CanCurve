:: NOT WORKING
:: plugin deployment help

:: setup environment
call %~dp0../env/activate_py.bat

ECHO on

SET PATH=C:\ProgramData\chocolatey\bin;%PATH%

:: change to plugin directory
cd %SRC_DIR%/%PROJ_NAME%



::It internally calls pyrcc5 to handle the conversion of .qrc files.
pb_tool zip

:: pyrcc5 -o resources.py resources.qrc

cmd.exe /k