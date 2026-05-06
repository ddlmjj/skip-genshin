@echo off
cd /d "%~dp0"

:: 1. Créer le venv s'il n'existe pas
if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

:: 2. Activer
call venv\Scripts\activate

:: 3. Installer/Mettre à jour les modules si requirements.txt existe
if exist "requirements.txt" (
    echo Verification des modules...
    pip install -r requirements.txt
)

:: 4. Lancer le script
python main.py

pause