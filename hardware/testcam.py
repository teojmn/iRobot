#!/usr/bin/env python3
"""
Script de test pour vérifier la caméra et la lecture de QR codes.
Affiche l'adresse e-mail lue depuis un QR code.
"""
import sys
import os

# Ajouter le chemin du module camera_handler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from camera_handler import CameraHandler

def main():
    print("=== Test de la caméra Raspberry Pi ===")
    print("Démarrage de la caméra...")
    
    cam = CameraHandler(
        camera_index=0,
        width=640,
        height=480,
        use_thread=True,
        decode_interval=0.1
    )
    
    try:
        cam.start()
        print("Caméra démarrée avec succès!")
        print("Présentez un QR code contenant une adresse e-mail (@epitech.eu ou @epitech.digital)...")
        print("Appuyez sur Ctrl+C pour quitter.\n")
        
        while True:
            # Attendre la détection d'un QR code (timeout de 1 seconde)
            qr_data = cam.wait_for_qr(timeout=1.0)
            
            if qr_data:
                for qr in qr_data:
                    if qr['type'] == 'EMAIL':
                        print(f"✓ Adresse e-mail détectée: {qr['data']}")
                    elif qr['type'] == 'NUMERIC':
                        print(f"  Code numérique détecté: {qr['data']}")
                print()
    
    except KeyboardInterrupt:
        print("\n\nArrêt du test...")
    except Exception as e:
        print(f"\nErreur: {e}")
        return 1
    finally:
        cam.stop()
        print("Caméra arrêtée.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())