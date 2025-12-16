import time

import cv2
import numpy as np
from picamera2 import Picamera2

def main():
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
    time.sleep(0.5)  # petit délai pour stabiliser exposition / focus

    # Initialisation du détecteur de QR OpenCV
    qr_detector = cv2.QRCodeDetector()

    print("=" * 50)
    print("Caméra lancée. Appuie sur Ctrl+C pour quitter.")
    print(f"Résolution: {video_config['main']['size']}")
    print("=" * 50)

    frame_count = 0
    detection_attempts = 0

    try:
        while True:
            frame_count += 1
            
            # Récupération d'une frame sous forme de numpy array
            frame = picam2.capture_array()
            
            print(f"\n[Frame {frame_count}] Capture réussie")
            print(f"  - Shape: {frame.shape}")
            print(f"  - Type: {frame.dtype}")

            # OpenCV travaille en BGR -> conversion
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            print(f"  - Conversion BGR OK")

            # Détection + décodage du QR code
            detection_attempts += 1
            print(f"  - Tentative de détection #{detection_attempts}...")
            
            data, points, straight_qrcode = qr_detector.detectAndDecode(frame_bgr)

            print(f"  - Résultat détection:")
            print(f"    * Data: '{data}'")
            print(f"    * Points: {points is not None and len(points) > 0}")
            if points is not None and len(points) > 0:
                print(f"    * Nombre de points: {len(points)}")
                print(f"    * Coordonnées: {points}")

            if points is not None and len(points) > 0:
                # Si `data` n'est pas vide, on a décodé quelque chose
                if data:
                    print("\n" + "!" * 50)
                    print(f"QR CODE DÉTECTÉ ET DÉCODÉ: {data}")
                    print("!" * 50)
                else:
                    print("  - QR code détecté mais non décodé (peut-être flou ou incomplet)")

            # Essayer aussi avec une conversion en niveaux de gris
            if frame_count % 5 == 0:  # tous les 5 frames
                gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                data_gray, points_gray, _ = qr_detector.detectAndDecode(gray)
                print(f"  - Test avec image en gris:")
                print(f"    * Data: '{data_gray}'")
                print(f"    * Points détectés: {points_gray is not None and len(points_gray) > 0}")

            time.sleep(0.1)  # petit délai pour éviter la surcharge CPU

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Arrêt du programme...")
        print(f"Total frames capturées: {frame_count}")
        print(f"Total tentatives de détection: {detection_attempts}")
        print("=" * 50)
    finally:
        # Nettoyage
        picam2.stop()
        picam2.close()

if __name__ == "__main__":
    main()