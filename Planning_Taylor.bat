@echo off

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call "~\env\Scripts\activate.bat"

REM Installer les modules nécessaires
echo Installation des modules nécessaires...
pip install pdfkit
pip install flask
pip install pandas
pip install numpy

REM Exécuter le serveur
echo Lancement du serveur...
python "Graphical_Interface\server.py"

REM Garder la fenêtre ouverte
pause