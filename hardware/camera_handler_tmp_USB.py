import time

import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image

def preprocess_for_qr(frame):
    """Prétraiter l'image pour améliorer la détection QR avec pyzbar"""
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 1. Égalisation d'histogramme pour améliorer le contraste
    equalized = cv2.equalizeHist(gray)
    
    # 2. Binarisation adaptative
    binary = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        blockSize=11, 
        C=2
    )
    
    # 3. Réduction du bruit
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # 4. Augmenter le contraste avec CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(gray)
    
    return gray, equalized, binary, denoised, clahe_img

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

    # Configuration de la résolution - RÉSOLUTION PLUS BASSE pour meilleure détection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # IMPORTANT: Désactiver l'autofocus pour éviter le flou
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    # Ajuster l'exposition pour un meilleur contraste
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)
    
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

    print("=" * 50)
    print("Webcam USB lancée. Appuie sur Ctrl+C pour quitter.")
    print(f"Résolution: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Backend: {cap.getBackendName()}")
    print("\nCONSEILS POUR LA DÉTECTION:")
    print("  - Placez le QR code à 20-30 cm de la caméra")
    print("  - Assurez un éclairage uniforme sans reflets")
    print("  - Tenez le QR code stable et bien visible")
    print("  - Évitez les inclinaisons importantes")
    print("=" * 50)

    frame_count = 0
    detection_attempts = 0
    error_count = 0
    successful_detections = 0

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
            
            error_count = 0
            
            print(f"\n[Frame {frame_count}] Capture réussie - Shape: {frame.shape}")

            # Appliquer plusieurs prétraitements
            detection_attempts += 1
            gray, equalized, binary, denoised, clahe_img = preprocess_for_qr(frame)
            
            # Tester avec plusieurs versions de l'image
            test_images = [
                ("Original RGB", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)),
                ("Grayscale", gray),
                ("Equalized Histogram", equalized),
                ("Adaptive Binary", binary),
                ("Denoised", denoised),
                ("CLAHE Enhanced", clahe_img),
            ]
            
            all_codes = []
            for name, img in test_images:
                pil_img = Image.fromarray(img)
                decoded = decode(pil_img)
                if decoded:
                    print(f"  ✓ {name}: {len(decoded)} code(s)")
                    all_codes.extend([(name, d) for d in decoded])
                else:
                    print(f"  ✗ {name}: 0 code")
            
            # Afficher les codes détectés
            if all_codes:
                successful_detections += 1
                unique_data = {}
                for method, d in all_codes:
                    data = d.data.decode('utf-8', errors='replace')
                    if data not in unique_data:
                        unique_data[data] = []
                    unique_data[data].append(method)
                
                print(f"\n" + "!" * 60)
                print(f"✓✓✓ {len(unique_data)} CODE(S) UNIQUE(S) DÉTECTÉ(S) ✓✓✓")
                for i, (data, methods) in enumerate(unique_data.items(), start=1):
                    print(f"\nCODE #{i}:")
                    print(f"  * Data: '{data}'")
                    print(f"  * Détecté par: {', '.join(set(methods))}")
                print(f"\nTaux de réussite: {successful_detections}/{detection_attempts} ({100*successful_detections/detection_attempts:.1f}%)")
                print("!" * 60)
            else:
                print("  → Aucun code détecté sur cette frame")
            
            # Sauvegarder des images de test périodiquement
            if frame_count % 30 == 0:
                timestamp = int(time.time())
                cv2.imwrite(f"debug_original_{timestamp}.jpg", frame)
                cv2.imwrite(f"debug_binary_{timestamp}.jpg", binary)
                cv2.imwrite(f"debug_clahe_{timestamp}.jpg", clahe_img)
                print(f"  → Images de debug sauvegardées (timestamp: {timestamp})")

            time.sleep(0.3)  # Délai pour laisser le temps de positionner le QR

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Arrêt du programme...")
        print(f"Total frames: {frame_count}")
        print(f"Total détections: {detection_attempts}")
        print(f"Détections réussies: {successful_detections}")
        if detection_attempts > 0:
            print(f"Taux de succès: {100*successful_detections/detection_attempts:.1f}%")
        print("=" * 50)
    finally:
        if cap is not None:
            cap.release()
        print("Webcam fermée")

if __name__ == "__main__":
    main()