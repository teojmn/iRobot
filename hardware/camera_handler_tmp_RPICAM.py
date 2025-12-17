import time

import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
from picamera2 import Picamera2

def main():
    print("Initialisation de la Raspberry Pi Camera...")
    
    # Initialisation Picamera2
    picam2 = Picamera2()

    # Configuration vidéo (résolution modérée pour accélérer le décodage)
    video_config = picam2.create_video_configuration(
        main={"size": (1280, 720)},  # tu peux baisser à (640, 480) si c'est lent
        buffer_count=4
    )
    picam2.configure(video_config)

    # Démarrage de la caméra
    picam2.start()
    
    print("Initialisation de la caméra...")
    time.sleep(2)  # Attendre que la caméra se stabilise

    print("=" * 50)
    print("Raspberry Pi Camera lancée. Appuie sur Ctrl+C pour quitter.")
    print(f"Résolution: {video_config['main']['size']}")
    print("Utilisation de pyzbar pour la détection de codes")
    print("=" * 50)

    frame_count = 0
    detection_attempts = 0
    error_count = 0

    try:
        while True:
            frame_count += 1
            
            # Récupération d'une frame sous forme de numpy array
            try:
                frame = picam2.capture_array()
            except Exception as e:
                error_count += 1
                print(f"\n[Frame {frame_count}] Erreur de capture! (Erreur #{error_count})")
                print(f"  - Exception: {e}")
                
                if error_count > 10:
                    print("Trop d'erreurs consécutives, arrêt du programme")
                    break
                
                time.sleep(0.5)
                continue
            
            error_count = 0  # Reset du compteur d'erreurs si succès
            
            print(f"\n[Frame {frame_count}] Capture réussie")
            print(f"  - Shape: {frame.shape}")
            print(f"  - Type: {frame.dtype}")
            print(f"  - Min/Max values: {frame.min()}/{frame.max()}")

            # Picamera2 capture en RGB par défaut
            print(f"  - Format: RGB (natif Picamera2)")

            # Détection + décodage du/des codes (pyzbar)
            detection_attempts += 1
            print(f"  - Tentative de détection #{detection_attempts}...")

            # Conversion directe en PIL Image (frame est déjà en RGB)
            pil_img = Image.fromarray(frame)

            decoded = decode(pil_img)
            print(f"  - Codes détectés: {len(decoded)}")

            if decoded:
                for i, d in enumerate(decoded, start=1):
                    data = d.data.decode('utf-8', errors='replace')
                    print(f"\n" + "!" * 30)
                    print(f"CODE #{i} DÉTECTÉ:")
                    print(f"  * Type : {d.type}")
                    print(f"  * Data : '{data}'")
                    print(f"  * Rect : {d.rect}")
                    print(f"  * Polygon points : {d.polygon}")
                    print("!" * 30)
            else:
                print("  - Aucun code décodé sur cette frame")

            # Essayer aussi avec une conversion en niveaux de gris tous les 5 frames
            if frame_count % 5 == 0:
                # Convertir RGB vers grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                pil_gray = Image.fromarray(gray)
                decoded_gray = decode(pil_gray)
                print(f"  - Test avec image en gris: {len(decoded_gray)} codes détectés")

            time.sleep(0.1)  # petit délai pour éviter la surcharge CPU

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Arrêt du programme...")
        print(f"Total frames capturées: {frame_count}")
        print(f"Total tentatives de détection: {detection_attempts}")
        print(f"Total erreurs: {error_count}")
        print("=" * 50)
    finally:
        # Nettoyage
        picam2.stop()
        picam2.close()
        print("Caméra fermée")

if __name__ == "__main__":
    main()