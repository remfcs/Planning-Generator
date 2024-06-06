@echo off
REM Chemin vers le fichier bash
set BASH_SCRIPT=%~dp0\bash_file\install.sh

REM Exécution du fichier bash
bash "%BASH_SCRIPT%"

REM Optionnel : Attendre une entrée pour fermer la fenêtre
pause
