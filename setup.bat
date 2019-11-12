@ECHO OFF

set "$py=false"
ECHO import sys; print('{0[0]}.{0[1]}'.format(sys.version_info^)^) >#.py
for /f "delims=" %%a in ('python #.py ^| findstr "3.7"') do set "$py=true"
del #.py
goto:%$py%

:false
ECHO Veuillez installer Python 3.7 et réessayer ...
pause > nul
exit/b

:true
ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
ECHO    Cr‚ation de l'environnement virtuel ...
ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
IF EXIST venv\ (
 echo venv directory already exists
) ELSE (
mkdir venv
)

python -m venv venv

CALL venv/Scripts/activate.bat

ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
ECHO    Installation des d‚pendances ...
ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
timeout 3 > nul
pip install -r requirements.txt

ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
ECHO    Transfert des ressources depuis disque partag‚ (Tesseract, dataset et graph TensorFlow entraŒn‚) ...
ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
timeout 3 > nul
robocopy "\\192.168.73.200\data$\Nantes\Echange de donn‚es\TensorFlow\Ressources Trad'UI" "%cd%" /E

ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
ECHO    Lancement de l'API Trad'UI sur le port 89 ...
ECHO. & ECHO ------------------------------------------------------------------------------------------------------------------------------------------------------ & ECHO.
timeout 3 > nul
python index.py