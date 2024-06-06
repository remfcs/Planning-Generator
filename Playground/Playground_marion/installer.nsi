; Définit le nom de l'installateur
OutFile "TestProgramInstaller.exe"

; Définit le répertoire d'installation par défaut
InstallDir "$PROGRAMFILES\TestProgram"

; Étapes de l'installateur
Page directory
Page instfiles

Section
    ; Définit le répertoire où les fichiers seront installés
    SetOutPath $INSTDIR
    
    ; Ajoutez les fichiers
    File "C:\Users\mario\Documents\EPF 4A\Projet\Planning-Generator\Playground_marion\README.md"
    File "C:\Users\mario\Documents\EPF 4A\Projet\Planning-Generator\Playground_marion\run_script.bat"
    File "C:\Users\mario\Documents\EPF 4A\Projet\Planning-Generator\Playground_marion\main.py"
    SetOutPath "$INSTDIR\templates"
    File "C:\Users\mario\Documents\EPF 4A\Projet\Planning-Generator\Playground_marion\templates\index.html"
    File "C:\Users\mario\Documents\EPF 4A\Projet\Planning-Generator\Playground_marion\templates\display_data.html"

    ; Ajoutez python.exe à l'installateur
    SetOutPath "$INSTDIR"
    File "C:\Users\mario\anaconda3\python.exe"
    File "C:\Users\mario\anaconda3\python311.dll"
    File "C:\Users\mario\anaconda3\zlib.dll"
    SetOutPath "$INSTDIR\encodings"
    File /r "C:\Users\mario\anaconda3\Lib\encodings\*.*"

    SetOutPath "$INSTDIR\bash_file"
    File "C:\Users\mario\Documents\EPF 4A\Projet\Planning-Generator\Playground_marion\bash_file\install.sh"

    ; Create Uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "Uninstall"
    Delete $INSTDIR\README.md
	Delete $INSTDIR\install.sh
	Delete $INSTDIR\run_script.bat
	Delete $INSTDIR\main.py
    Delete $INSTDIR\web2.py
    Delete $INSTDIR\templates\index.html
    Delete $INSTDIR\templates\display_data.html
    RMDir $INSTDIR\templates
	Delete $INSTDIR\zlib.dll
	Delete $INSTDIR\python311.dll
	Delete $INSTDIR\python.exe
    RMDir /r $INSTDIR\encodings
    Delete $INSTDIR\encodings\__pycache__\*
    RMDir $INSTDIR\encodings\__pycache__
	RMDir $INSTDIR\encodings
    Delete $INSTDIR\bash_file\install.sh
    RMDir $INSTDIR\bash_file
    Delete $INSTDIR\Uninstall.exe
	RMDir $INSTDIR   ; Remove the installation directory if empty
    SetOutPath $INSTDIR\..   ; Supprimer le répertoire d'installation parent s'il est vide
    RMDir $INSTDIR\..
SectionEnd