#!/bin/bash

echo "--- Arrêt du système iRobot ---"

# Tue le gestionnaire RFID d'abord (il utilise le speaker)
pkill -f "hardware/rfid_manager.py" 2>/dev/null || true

# Attendre que le processus se termine proprement
sleep 2

# Tue le serveur Flask
fuser -k 5000/tcp 2>/dev/null || true

# Forcer la libération des ressources ALSA/audio
sudo fuser -k /dev/snd/* 2>/dev/null || true
sudo killall -9 pulseaudio 2>/dev/null || true

# Réinitialiser le module audio
sudo modprobe -r snd_usb_audio 2>/dev/null || true
sudo modprobe snd_usb_audio 2>/dev/null || true

echo "✓ Système arrêté."