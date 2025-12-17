import cv2
import time

def find_usb_camera():
    """Recherche automatiquement la webcam USB disponible"""
    print("Recherche de la webcam USB...")
    
    for i in range(5):
        print(f"  Essai de /dev/video{i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  ✓ Webcam trouvée sur /dev/video{i}")
                return cap
            cap.release()
    
    return None

# Recherche automatique de la webcam USB
cap = find_usb_camera()

if cap is None:
    print("\n" + "=" * 50)
    print("Erreur: Impossible d'ouvrir la webcam USB")
    print("Vérifications à faire:")
    print("  1. Vérifiez que la webcam est branchée: lsusb")
    print("  2. Vérifiez les périphériques vidéo: ls -la /dev/video*")
    print("  3. Vérifiez les permissions: sudo usermod -a -G video $USER")
    print("=" * 50)
    exit(1)

# Configuration optimale pour QR codes
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Désactiver l'autofocus
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Réduire la latence

# Récupération des infos caméra
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# QR code detection Method
detector = cv2.QRCodeDetector()

print("=" * 50)
print("Caméra initialisée. Scannez un QR code (Ctrl+C pour quitter)")
print(f"Résolution: {width}x{height}")
print("\nCONSEILS:")
print("  - Placez le QR code à 20-30 cm de la caméra")
print("  - Assurez un bon éclairage")
print("  - Tenez le QR code stable")
print("=" * 50)

# Stabilisation de la caméra
print("\nInitialisation...")
time.sleep(2)
for _ in range(5):
    cap.read()  # Vider le buffer initial

frame_count = 0
detections_count = 0

try:
    while True:
        frame_count += 1
        
        # Capture de l'image
        ret, img = cap.read()
        
        if not ret or img is None:
            print(f"[Frame {frame_count}] Erreur de lecture")
            time.sleep(0.5)
            continue
        
        # Détection QR code
        data, bbox, _ = detector.detectAndDecode(img)
        
        # Affichage du résultat
        if bbox is not None and data:
            detections_count += 1
            print(f"\n{'!' * 50}")
            print(f"[Frame {frame_count}] ✓ QR CODE DÉTECTÉ!")
            print(f"Data: '{data}'")
            print(f"Total détections: {detections_count}")
            print('!' * 50)
            
            # Logique métier
            if data == 'red':
                print("→ Action RED détectée")
            elif data == 'green':
                print("→ Action GREEN détectée")
            
            # Pause courte pour éviter les détections multiples
            time.sleep(1)
        else:
            # Affichage périodique pour confirmer que ça tourne
            if frame_count % 30 == 0:
                print(f"[Frame {frame_count}] En attente de QR code...")
        
        time.sleep(0.1)  # Petit délai pour ne pas surcharger le CPU

except KeyboardInterrupt:
    print("\n" + "=" * 50)
    print("Arrêt de la détection")
    print(f"Total frames: {frame_count}")
    print(f"Total détections: {detections_count}")
    print("=" * 50)
finally:
    cap.release()
    print("Caméra libérée")