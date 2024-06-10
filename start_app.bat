@echo off

rem Définir le chemin relatif basé sur le répertoire du script
set SCRIPT_DIR=%~dp0
set ORIGINAL_SCRIPT_DIR=%~dp0

rem Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call "%SCRIPT_DIR%env\Scripts\activate.bat"


rem Utiliser pip et python de l'environnement virtuel
set PIP_PATH=%ORIGINAL_SCRIPT_DIR%env\Scripts\pip.exe
set PYTHON_PATH=%ORIGINAL_SCRIPT_DIR%env\Scripts\python.exe

rem Installation des modules nécessaires dans l'environnement virtuel
echo Installation des modules nécessaires...
"%PIP_PATH%" install pdfkit flask pandas numpy

rem Vérifier l'existence du fichier server.py
if not exist "%ORIGINAL_SCRIPT_DIR%Graphical_Interface\server.py" (
    echo Le fichier server.py n'a pas été trouvé.
    pause
    exit /b 1
)

rem Exécuter le serveur
echo Lancement du serveur...
"%PYTHON_PATH%" "%ORIGINAL_SCRIPT_DIR%Graphical_Interface\server.py"

rem Vérifier si le serveur s'est lancé correctement
if errorlevel 1 (
    echo Erreur lors du lancement du serveur.
    pause
    exit /b 1
)
echo Serveur lancé avec succès.

rem Garder la fenêtre ouverte
pause
