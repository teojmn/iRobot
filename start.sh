#!/bin/bash

# 1. Aller dans le dossier du projet
cd /home/GITHUB/iRobot

# 2. Corriger les permissions une bonne fois pour toutes
echo "--- Configuration des permissions ---"
sudo chown -R hdmi-locker:hdmi-locker data/
chmod -R 755 data/

# 3. Nettoyer les anciens processus au cas où
echo "--- Nettoyage des anciens processus ---"
fuser -k 5000/tcp 2>/dev/null || true
pkill -f "hardware/rfid_manager.py" 2>/dev/null || true

# 4. Lancer le système
echo "--- Lancement du système iRobot ---"
source .venv/bin/activate
# On lance le web en arrière-plan et le RFID au premier plan
python web/app.py & python hardware/rfid_manager.py
