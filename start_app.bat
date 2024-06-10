@echo off

REM Vérifier l'existence du script d'activation
if not exist "C:\planning-generator\env\Scripts\activate.bat" (
    echo Le script d'activation n'a pas été trouvé.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call "C:\planning-generator\env\Scripts\activate.bat"

REM Vérifier si l'environnement virtuel est activé
if errorlevel 1 (
    echo Erreur lors de l'activation de l'environnement virtuel.
    pause
    exit /b 1
)
echo Environnement virtuel activé avec succès.

REM Installer les modules nécessaires
echo Installation des modules nécessaires...
pip install pdfkit
pip install flask
pip install pandas
pip install numpy

REM Vérifier si pip a réussi
if errorlevel 1 (
    echo Erreur lors de l'installation des modules.
    pause
    exit /b 1
)
echo Modules installés avec succès.

REM Exécuter le serveur
echo Lancement du serveur...
python "C:\planning-generator\Graphical_Interface\server.py"

REM Vérifier si le serveur s'est lancé correctement
if errorlevel 1 (
    echo Erreur lors du lancement du serveur.
    pause
    exit /b 1
)
echo Serveur lancé avec succès.

REM Garder la fenêtre ouverte
pause
    