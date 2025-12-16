import time

import cv2
import numpy as np

def main():
    print("Recherche de la webcam USB...")
    
    # Tester plusieurs indices de caméra
    cap = None
    for i in range(5):
        print(f"Essai de /dev/video{i}...")
        test_cap = cv2.VideoCapture(i)
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret and frame is not None:
                print(f"✓ Webcam trouvée sur /dev/video{i}")
                cap = test_cap
                break
            else:
                test_cap.release()
        else:
            test_cap.release()
    
    if cap is None:
        print("\n" + "=" * 50)
        print("Erreur: Impossible d'ouvrir la webcam USB")
        print("Vérifications à faire:")
        print("  1. Vérifiez que la webcam est branchée: lsusb")
        print("  2. Vérifiez les périphériques vidéo: ls -la /dev/video*")
        print("  3. Vérifiez les permissions: sudo usermod -a -G video $USER")
        print("  4. Essayez: sudo chmod 666 /dev/video0")
        print("=" * 50)
        return

    # Configuration de la résolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # Attendre que la caméra se stabilise
    print("Initialisation de la caméra...")
    time.sleep(2)
    
    # Vider le buffer initial
    for _ in range(5):
        cap.read()
    
    # Récupération de la résolution réelle
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Initialisation du détecteur de QR OpenCV
    qr_detector = cv2.QRCodeDetector()

    print("=" * 50)
    print("Webcam USB lancée. Appuie sur Ctrl+C pour quitter.")
    print(f"Résolution: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Backend: {cap.getBackendName()}")
    print("=" * 50)

    frame_count = 0
    detection_attempts = 0
    error_count = 0

    try:
        while True:
            frame_count += 1
            
            # Récupération d'une frame
            ret, frame = cap.read()
            
            if not ret or frame is None:
                error_count += 1
                print(f"\n[Frame {frame_count}] Erreur de capture! (Erreur #{error_count})")
                print(f"  - ret: {ret}")
                print(f"  - frame is None: {frame is None}")
                
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
        print(f"Total erreurs: {error_count}")
        print("=" * 50)
    finally:
        # Nettoyage
        if cap is not None:
            cap.release()
        print("Webcam fermée")

if __name__ == "__main__":
    main()