#!/bin/bash

echo "--- Arrêt du système iRobot ---"

# Tue le serveur Flask
fuser -k 5000/tcp 2>/dev/null || true

# Tue le gestionnaire RFID
pkill -f "hardware/rfid_manager.py" 2>/dev/null || true

echo "✓ Système arrêté."