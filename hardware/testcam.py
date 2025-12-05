import cv2
from pyzbar.pyzbar import decode

def read_qr_code():
    """Lit un QR code depuis la caméra."""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra")
        return
    
    print("Détection de QR code en cours (Ctrl+C pour quitter)...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erreur de lecture de la frame")
                break
            
            # Décoder les QR codes
            for obj in decode(frame):
                print(f"Email détecté: {obj.data.decode('utf-8')}")
                
    except KeyboardInterrupt:
        print("\nArrêt de la détection")
    finally:
        cap.release()

if __name__ == "__main__":
    read_qr_code()