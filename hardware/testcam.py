import cv2
from pyzbar.pyzbar import decode
import time

def read_qr_code():
    """Lit un QR code depuis la caméra."""
    # Essayer différents indices de caméra avec backend spécifique
    for index in range(3):
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if cap.isOpened():
            # Configurer la résolution (important pour Raspberry Pi)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Tester la capture
            ret, test_frame = cap.read()
            if ret:
                print(f"Caméra trouvée et fonctionnelle à l'index {index}")
                break
            else:
                print(f"Caméra à l'index {index} ne peut pas capturer")
        cap.release()
    else:
        print("Erreur: Aucune caméra fonctionnelle trouvée")
        return
    
    # Laisser le temps à la caméra de s'initialiser
    time.sleep(1)
    
    print("Détection de QR code en cours (Ctrl+C pour quitter)...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erreur de lecture, reconnexion...")
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
                continue
            
            # Décoder les QR codes
            for obj in decode(frame):
                print(f"Email détecté: {obj.data.decode('utf-8')}")
                
    except KeyboardInterrupt:
        print("\nArrêt de la détection")
    finally:
        cap.release()

if __name__ == "__main__":
    read_qr_code()