import time

import cv2
import numpy as np

def main():
    # Initialisation de la webcam USB (généralement /dev/video0)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la webcam USB")
        print("Vérifiez que la webcam est bien branchée et détectée")
        print("Utilisez 'ls /dev/video*' pour voir les périphériques disponibles")
        return

    # Configuration de la résolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Récupération de la résolution réelle
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialisation du détecteur de QR OpenCV
    qr_detector = cv2.QRCodeDetector()

    print("=" * 50)
    print("Webcam USB lancée. Appuie sur Ctrl+C pour quitter.")
    print(f"Résolution: {width}x{height}")
    print("=" * 50)

    frame_count = 0
    detection_attempts = 0

    try:
        while True:
            frame_count += 1
            
            # Récupération d'une frame
            ret, frame = cap.read()
            
            if not ret:
                print(f"\n[Frame {frame_count}] Erreur de capture!")
                continue
            
            print(f"\n[Frame {frame_count}] Capture réussie")
            print(f"  - Shape: {frame.shape}")
            print(f"  - Type: {frame.dtype}")

            # La webcam USB capture déjà en BGR, pas besoin de conversion
            print(f"  - Format: BGR (natif webcam USB)")

            # Détection + décodage du QR code
            detection_attempts += 1
            print(f"  - Tentative de détection #{detection_attempts}...")
            
            data, points, straight_qrcode = qr_detector.detectAndDecode(frame)

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
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
        cap.release()
        print("Webcam fermée")

if __name__ == "__main__":
    main()