import time

import cv2
import numpy as np

def main():
    print("Recherche des webcams disponibles...")
    
    # Test de plusieurs indices de caméra
    for i in range(5):
        test_cap = cv2.VideoCapture(i)
        if test_cap.isOpened():
            print(f"  - Webcam trouvée à l'index {i}")
            test_cap.release()
        else:
            print(f"  - Pas de webcam à l'index {i}")
    
    print("\nTentative d'ouverture de la webcam...")
    
    # Essayer différentes méthodes d'ouverture
    # Méthode 1: index simple
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("  Index 0 échoué, essai avec V4L2...")
        # Méthode 2: forcer V4L2 sur Linux
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print("  V4L2 échoué, essai index 1...")
        # Méthode 3: essayer index 1
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("\nErreur: Impossible d'ouvrir la webcam USB")
        print("Vérifications à faire:")
        print("  1. La webcam est-elle branchée? (lsusb)")
        print("  2. Les périphériques vidéo existent-ils? (ls -l /dev/video*)")
        print("  3. Avez-vous les permissions? (sudo usermod -a -G video $USER)")
        print("  4. La webcam est-elle utilisée par un autre programme?")
        return

    print("Webcam ouverte avec succès!")

    # Configuration de la résolution avec gestion d'erreur
    print("\nConfiguration de la résolution...")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Récupération de la résolution réelle
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Test de capture initiale
    print("Test de capture initiale...")
    for i in range(5):
        ret, test_frame = cap.read()
        if ret:
            print(f"  - Test capture {i+1}/5: OK")
            break
        else:
            print(f"  - Test capture {i+1}/5: Échec, nouvelle tentative...")
            time.sleep(0.5)
    
    if not ret:
        print("\nErreur: Impossible de capturer des images de la webcam")
        cap.release()
        return

    # Initialisation du détecteur de QR OpenCV
    qr_detector = cv2.QRCodeDetector()

    print("\n" + "=" * 50)
    print("Webcam USB lancée. Appuie sur Ctrl+C pour quitter.")
    print(f"Résolution: {width}x{height}")
    print(f"FPS: {fps}")
    print("=" * 50)

    frame_count = 0
    detection_attempts = 0
    error_count = 0

    try:
        while True:
            frame_count += 1
            
            # Récupération d'une frame
            ret, frame = cap.read()
            
            if not ret:
                error_count += 1
                print(f"\n[Frame {frame_count}] Erreur de capture! (erreur #{error_count})")
                
                if error_count > 10:
                    print("Trop d'erreurs de capture consécutives, arrêt du programme")
                    break
                
                time.sleep(0.5)
                continue
            
            # Reset du compteur d'erreurs si capture réussie
            error_count = 0
            
            print(f"\n[Frame {frame_count}] Capture réussie")
            print(f"  - Shape: {frame.shape}")
            print(f"  - Type: {frame.dtype}")
            print(f"  - Min/Max values: {frame.min()}/{frame.max()}")

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
        print(f"Total erreurs de capture: {error_count}")
        print("=" * 50)
    finally:
        # Nettoyage
        cap.release()
        print("Webcam fermée")

if __name__ == "__main__":
    main()