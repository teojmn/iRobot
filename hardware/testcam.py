import cv2
from pyzbar.pyzbar import decode
import time

def read_qr_code():
    """Lit un QR code depuis la caméra."""
    # Essayer différents indices de caméra
    for index in range(3):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Caméra trouvée à l'index {index}")
            break
        cap.release()
    else:
        print("Erreur: Aucune caméra trouvée")
        return
    
    # Laisser le temps à la caméra de s'initialiser
    time.sleep(2)
    
    print("Détection de QR code en cours (Ctrl+C pour quitter)...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erreur de lecture de la frame")
                time.sleep(0.5)
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