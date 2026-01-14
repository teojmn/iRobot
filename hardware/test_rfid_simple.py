#!/usr/bin/env python3
"""
Script de test simple pour vérifier la lecture RFID
Affiche l'UID de chaque carte détectée
"""

import time
from mfrc522 import SimpleMFRC522

print("=== Test Lecteur RFID ===")
print("Approchez une carte du lecteur...")
print("Appuyez sur Ctrl+C pour arrêter\n")

reader = SimpleMFRC522()

try:
    while True:
        print("En attente d'une carte...")
        
        # Lecture bloquante (attend qu'une carte soit détectée)
        uid, text = reader.read()
        
        print(f"✓ Carte détectée !")
        print(f"  UID: {uid}")
        print(f"  Texte: {text}")
        print("-" * 40)
        
        # Pause pour éviter de lire plusieurs fois la même carte
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\nArrêt du test.")
finally:
    print("Nettoyage GPIO...")
    # Le nettoyage est géré automatiquement par SimpleMFRC522