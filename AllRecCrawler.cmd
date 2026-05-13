@echo off
set /a savereq=0
cd %~dp0
set "applock=arc.lock"
set "verstr=1.1"
TITLE AllRecipes v%verstr%
cls
if exist "%applock%" (
    echo RecipeApp already running!
    echo.
    echo If this is a mistake, you may not have
    echo shutdown a session properly. Please
    echo delete '%applock%' to fix.
    echo.
    pause
    exit /b
)
echo Please wait...
echo.
if NOT exist "%~dp0python\Scripts\pip.exe" (
	%~dp0python\python.exe "%~dp0python\get-pip.py" --no-warn-script-location
)
%~dp0python\python.exe -m pip cache purge
cls
echo Please wait...
if NOT exist "%~dp0.allrec\" (
	%~dp0python\python.exe -m pip install virtualenv --no-warn-script-location
	%~dp0python\python.exe -m virtualenv .allrec
	call .allrec\Scripts\activate
) else (
	rem Error prevention, just in case
	call .allrec\Scripts\deactivate
	call .allrec\Scripts\activate
)
cls
echo Please wait...
python -m pip install --upgrade pip
echo running > "%applock%"
cls
python "%~dp0arc.py"
echo.
if %savereq% == 1 (
	python -m pip freeze --local > "%~dp0requirements.txt"
)
del "%~dp0%applock%"
call .allrec\Scripts\deactivate
rem echo.
echo It is now safe to close this window
pause >nul
exit /b
